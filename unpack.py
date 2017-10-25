from array import array as array
import crayfis_data_pb2 as cray
import numpy            as np
import os               as os
import ROOT             as R

OK  = 0
ERR = 1

def getType( field_descriptor ):
        def makeDic( type, code ):
            return { 'type' : type, 'code' : code }

        f  = field_descriptor
        if   f.type == f.TYPE_BOOL:
            return makeDic( 'Bool_t'   , 'O' )
        elif f.type == f.TYPE_BYTES:
            return makeDic( 'BYTES'    , ''  )
        elif f.type == f.TYPE_FLOAT:
            return makeDic( 'Float_t'  , 'F' )
        elif f.type == f.TYPE_DOUBLE:
            return makeDic( 'Double_t' , 'D' )
        elif f.type == f.TYPE_INT32 or f.type == f.TYPE_SINT32:
            return makeDic( 'Int_t'    , 'I' )
        elif f.type == f.TYPE_UINT32:
            return makeDic( 'UInt_t'   , 'i' )
        elif f.type == f.TYPE_INT64 or f.type == f.TYPE_SINT64:
            return makeDic( 'Long64_t' , 'L' )
        elif f.type == f.TYPE_UINT64:
            return makeDic( 'ULong64_t', 'l' )
        elif f.type == f.TYPE_STRING:
            return makeDic( 'STRING'   , 'C' )
        elif f.type == f.TYPE_MESSAGE:
            return makeDic( 'MESSAGE'  , ''  )
        elif f.type == f.TYPE_ENUM:
            return makeDic( 'ENUM'     , ''  )
        elif f.type == f.TYPE_GROUP:
            return makeDic( 'GROUP'    , ''  )
        else:
            return makeDic( ''         , ''  )

# Each structure:  [  [ declaration e.g. Int_t, code e.g. I ], field name (string), field value ]
def getDic( field_value ):
    typenameval = [ { 'typecode' : getType(f), 'name' : f.name, 'value' : v } for [f,v] in field_value.ListFields() ]
    basics      = [ b for b in typenameval if b['typecode']['code'] != ''        ]
    bytes       = [ b for b in typenameval if b['typecode']['type'] == 'BYTES'   ]
    messages    = [ m for m in typenameval if m['typecode']['type'] == 'MESSAGE' ]
    enums       = [ e for e in typenameval if e['typecode']['type'] == 'ENUM'    ]
    n_other     = len(typenameval) - len(basics) - len(bytes) - len(messages) - len(enums)

    assert n_other == 0
    return { 'basics' : basics, 'bytes' : bytes, 'messages' : messages, 'enums' : enums }

# container = { 'var name' : numpy array len(data) of dtype }
# updates container value for 'var name' if it exists
# otherwise creates key and value pair
# for strings, adds '\0' termination character
def saveBasics( vars, container ):
    for basic in vars:
        # too big for long (exposure_block)
        if  basic['name'    ] == 'run_id' and basic['typecode']['code'] == 'l':
            basic['name'    ] = 'run_id_block'
            basic['typecode'] = { 'type' : 'STRING', 'code' : 'C' }
            basic['value'   ] = str( basic['value'] )

        # too big for long (run_config)
        if  basic['name'] == 'id_hi' or basic['name'] == 'id_lo':
            basic['typecode'] = { 'type' : 'STRING', 'code' : 'C' }
            basic['value'   ] = str( basic['value'] )

        if not basic['name'] in container.keys():
            container[ basic['name'] ] = { 'value' : np.zeros( 1, dtype=type( basic['value'] ) ), 'code' : basic['typecode']['code'] }

        if basic['typecode']['type'] == 'STRING':
            container[ basic['name'] ] = { 'value' : array('c', str(basic['value']) + '\0'), 'code' : basic['typecode']['code'] }
        else:
            try:
                container[ basic['name'] ]['value'][0] = basic['value']
            except Exception, e:
                print
                print '\tException {0}:'.format( container['tarfile']['value'].tostring() )
                print '\t\t{0}'.format(e)
                print '\t\tDebug info: {0} doesnt work for {1} type for {2}'.format( basic['value'], basic['typecode']['type'],basic['name'] )
                print '\tWARNING: setting value to 0 and moving on...'
                container[ basic['name'] ]['value'][0] = 0                
                
# container = { 'var name' : R.vector(type) }
def saveVectors( vars, container ):
    for vector in vars:
        if not vector['name'] in container.keys():
            container[ vector['name'] ] = { 'value' : R.vector( vector['typecode']['type'] )(), 'code' : '' }
        container[ vector['name'] ]['value'].push_back( vector['value'] )
        
def clearVectors( basics ):
    for key, dic in basics.iteritems():
        if str( type(dic['value']) ).find( 'ROOT.vector' ) >= 0:
            dic['value'].clear()

def openFile( basics, export_path ):
    assert 'device_id' in basics.keys()
    path = os.path.join( export_path, basics['device_id']['value'].tostring().strip('\0') + '.root' )
    if not os.path.isfile( path ):
        file = R.TFile( path, 'create' )
        file.mkdir( 'exposure_blocks', 'exposure_blocks description' )
        file.mkdir( 'run_configs', 'run_configs description' )
        file.mkdir( 'calibration_results', 'calibration_restuls description' )
        file.Close()
    return R.TFile( path, 'update' )
  
def fillTree( basics, tree ):
    ordered = [ [key, dic] for [key, dic] in basics.iteritems() ]
    ordered = sorted( ordered, key=lambda k: k[0].lower() )

    branches = [ branch.GetName() for branch in tree.GetListOfBranches() ]
    for key, dic in ordered:
        if key in branches:
            tree.SetBranchAddress( str(key), dic['value'] )
        else:
            if dic['code'] == '':
                tree.Branch( str(key), dic['value'] )
            else:
                tree.Branch( str(key), dic['value'], key + '/' + dic['code'] )
    tree.Fill()

def Pixel( pixel, basics ):
    pixel_dic      = getDic( pixel )
    pixel_basics   = pixel_dic['basics'  ]
    pixel_bytes    = pixel_dic['bytes'   ]
    pixel_messages = pixel_dic['messages']
    pixel_enums    = pixel_dic['enums'   ]
    
    # assert expected structure: pixel basics only (at last)
    assert len( pixel_bytes )    == 0
    assert len( pixel_messages ) == 0
    assert len( pixel_enums )    == 0

    saveVectors( pixel_basics, basics )

def Event( event, basics, tree ):
    event_dic      = getDic( event )
    event_basics   = event_dic['basics'  ]
    event_bytes    = event_dic['bytes'   ]
    event_messages = event_dic['messages']
    event_enums    = event_dic['enums'   ]
    
    # assert expect structure: event basics and messages
    assert len( event_bytes ) == 0
    assert len( event_enums ) == 0
    
    saveBasics( event_basics, basics )
    
    for message in event_messages:
        assert message['name'] == 'pixels'
        for pixel in message['value']:
            Pixel( pixel, basics )
        fillTree( basics, tree )
        clearVectors( basics )

def ExposureBlock( exposure_block, basics ):
    block_dic      = getDic( exposure_block )
    block_basics   = block_dic['basics'  ]
    block_bytes    = block_dic['bytes'   ]
    block_messages = block_dic['messages']
    block_enums    = block_dic['enums'   ]
    
    # assert expected structure: exposure_block basics, messages, and one enum
    assert len( block_bytes ) == 0
    if len( block_enums ) == 0:
        print
        print '\tskipping {0}, block_enums missing'.format( basics['tarfile']['value'].tostring() )
        return ERR
    assert len( block_enums ) == 1
    assert block_enums[0]['name'] == 'daq_state'

    v = ''
    if   block_enums[0]['value'] == 0:
        v = 'INIT'
    elif block_enums[0]['value'] == 1:
        v = 'CALIBRATION'
    elif block_enums[0]['value'] == 2:
        v = 'DATA'
    else:
        print
        print '\tskipping {0}, invalid block_enum'.format( basics['tarfile']['value'].tostring() )
        return ERR    
    block_basics.append( { 'typecode' : {'type':'STRING', 'code':'C'}, 'name' : 'daq_state', 'value' : v } )

    saveBasics( block_basics, basics )
    
    assert 'start_time' in basics.keys()
    assert 'end_time'   in basics.keys()
    d_keys = [ key.GetName() for key in R.gDirectory.GetListOfKeys() ]
    if str(basics['start_time']['value'][0]) in d_keys:
        print
        print '\tskipping {0}, exposure_block exists'.format( basics['tarfile']['value'].tostring() )
        return ERR
    tree = R.TTree( str( basics['start_time']['value'][0] ), 
                    str( basics['end_time']  ['value'][0] ) )

    for message in block_messages:
        assert message['name'] == 'events'
        for event in message['value']:
            Event( event, basics, tree )
    tree.Write('', R.TObject.kOverwrite)
    return OK
    
def RunConfig( run_config, basics ):
    config_dic      = getDic( run_config )
    config_basics   = config_dic['basics'  ]
    config_bytes    = config_dic['bytes'   ]
    config_messages = config_dic['messages']
    config_enums    = config_dic['enums'   ]
    
    # assert expected structure: run_config basics only
    assert len( config_bytes    ) == 0
    assert len( config_messages ) == 0
    assert len( config_enums    ) == 0

    for i, basic in enumerate(config_basics):
        if basic['name'].find('_params') >= 0:
            string = basic['value'].strip('\0')
            delimiter = ';'
            if string.find(', android.') != -1:
                delimiter = ', '
            for j, token in enumerate(string.split(delimiter)):
                token.strip()
                if token == '':
                    continue
                subdelimiter = '='
                if delimiter == ', ':
                    subdelimiter = ':'
                if len(token.split(subdelimiter)) != 2:
                    print
                    print '\tERROR: unpack.py, anomalous field delimitation: ' + token
                    print '\t\t repair: adding to end of ' + config_basics[-1]['name'] + ': ' + config_basics[-1]['value'] + delimiter + token
                    config_basics[-1]['value'] += delimiter + token 
                    continue
                newkey, newval = token.split(subdelimiter)
                config_basics.append( { 'typecode' : {'type':'STRING', 'code':'C'}, 'name' : newkey.replace('-','_'), 'value' : newval } )
            config_basics.pop(i)

    saveBasics( config_basics, basics )

    assert 'start_time'    in basics.keys()
    assert 'crayfis_build' in basics.keys()
    d_keys = [ key.GetName() for key in R.gDirectory.GetListOfKeys() ]
    if str(basics['start_time']['value'][0]) in d_keys:
        print
        print '\tskipping {0}, run_config exists'.format( basics['tarfile']['value'].tostring() )
        return ERR
    tree = R.TTree( str( basics['start_time'   ]['value'][0] ), 
                         basics['crayfis_build']['value'].tostring().strip('\0') )

    fillTree( basics, tree )
    tree.Write('', R.TObject.kOverwrite)
    return OK
    
def CalibrationResults( calibration_results, basics ):
    results_dic      = getDic( calibration_results )
    results_basics   = results_dic['basics'  ]
    results_bytes    = results_dic['bytes'   ]
    results_messages = results_dic['messages']
    results_enums    = results_dic['enums'   ]
    
    # assert expected structure: calibration_results basics only
    assert len( results_bytes    ) == 0
    assert len( results_messages ) == 0
    assert len( results_enums    ) == 0

    for i, basic in enumerate(results_basics):
        if str( type(basic['value']) ).find('google.protobuf.') >= 0:
            arr = [ val for val in basic['value'] ]
            typ = str(type( basic['value'][0] )).split("'")[1]
            v = R.vector( typ )()
            for a in arr:
                v.push_back(a)
            basics[ basic['name'] ]  = { 'value' : v, 'code' : '' }
            results_basics.pop(i)
    saveBasics( results_basics, basics )

    assert 'submit_time' in basics.keys()
    d_keys = [ key.GetName() for key in R.gDirectory.GetListOfKeys() ]
    if str(basics['submit_time']['value'][0]) in d_keys:
        print
        print '\tskipping {0}, calibration_result exists'.format( basics['tarfile']['value'].tostring() )
        return ERR
    tree = R.TTree( str( basics['submit_time']['value'][0] ), 'submit_time' )

    fillTree( basics, tree )
    tree.Write('', R.TObject.kOverwrite)
    return OK
    
def CrayonMessage( crayon_message, basics, export_path ):
    crayon_message.seek(0)

    crayon          = cray.CrayonMessage.FromString( crayon_message.read() )
    crayon_dic      = getDic( crayon )
    crayon_basics   = crayon_dic['basics'  ]
    crayon_bytes    = crayon_dic['bytes'   ]
    crayon_messages = crayon_dic['messages']
    crayon_enums    = crayon_dic['enums'   ]

    # assert expected structure: basics and bytes by the name of 'payload'
    assert len( crayon_messages )  == 0
    assert len( crayon_enums    )  == 0
    if len( crayon_bytes ) == 0:
        print
        print '\tskipping {0}, no payload'.format( basics['tarfile']['value'].tostring() )
        return
    if len( crayon_bytes) > 1:
        print
        print '\tERROR {0}, multiple payloads, skipping'.format( basics['tarfile']['value'].tostring() )
        return
    assert crayon_bytes[0]['name'] == 'payload'

    saveBasics( crayon_basics, basics )    
    file = openFile( basics, export_path )

    payload = ''
    try:
        payload = cray.DataChunk.FromString( crayon_bytes[0]['value'] )
    except Exception, e:
        print
        print '\tException {0}:'.format( basics['tarfile']['value'].tostring() )
        print '\t\t{0}'.format(e)
        print '\t\tDebug crayon_bytes[0][value][-50:] = {0}'.format( str(crayon_bytes[0]['value'])[-50:] )
        print '\tskipping'
        file.Close()
        return
    payload_dic      = getDic( payload )
    payload_basics   = payload_dic['basics'  ]
    payload_bytes    = payload_dic['bytes'   ]
    payload_messages = payload_dic['messages']
    payload_enums    = payload_dic['enums'   ]
    
    # assert expected structure: payload contains only messages
    assert len( payload_basics )  == 0
    assert len( payload_bytes  )  == 0
    assert len( payload_enums  )  == 0
    
    if len( payload_messages ) == 0:
        print
        print '\tskipping {0}, empty payload'.format( basics['tarfile']['value'].tostring() )
        file.Close()
        return
            
    errors = 0
    for message in payload_messages:
        assert file.cd( message['name'] )

        if message['name'] == 'exposure_blocks':
            for block in message['value']:
                errors += ExposureBlock( block, basics )
        elif message['name'] == 'run_configs':
            for config in message['value']:
                errors += RunConfig( config, basics )
        elif message['name'] == 'calibration_results':
            for results in message['value']:
                errors += CalibrationResults( results, basics )
        else:
            print
            print '\tskipping {0}, unknown payload'.format( basics['tarfile']['value'].tostring() )
            file.Close()
            return        

    file.Close()
