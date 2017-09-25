import errno            as errno
import os               as os
import ROOT             as R
import sys              as sys

if len(sys.argv) != 3:
    print '>> sausage: python loom.py import_path export_path'
    sys.exit()

import_path = sys.argv[1]
export_path = sys.argv[2]

rootfiles   = []
for path, directories, files in os.walk( import_path ):
    for filename in files:
        if filename.endswith('.root'):
            rootfiles.append( [path, filename] )
rootfiles = sorted( rootfiles, key=lambda k: [ k[1].lower(), k[0].lower() ], reverse=True )

todo = {}
for path, device in rootfiles:
    if not device in todo.keys():
        todo[device] = []
    todo[device].append( path )

for device, paths in todo.items():
    print
    print device
    
    if os.path.exists( os.path.join(export_path, device) ):
        print '\t> skipping {0}'.format( os.path.join( export_path, device ) )
        continue

    outfile = R.TFile( os.path.join( export_path, device ), 'create' )
    outfile.mkdir( 'exposure_blocks', 'exposure_blocks description' )
    outfile.mkdir( 'run_configs', 'run_configs description' )
    outfile.mkdir( 'calibration_results', 'calibration_results description' )
    outfile.Close()

    e_keys  = []
    r_keys  = []
    c_keys  = []
    infiles = []
    for path in paths:
        print '\t' + path 

        infiles.append( R.TFile( os.path.join( path, device ) ) )
        for e_key in infiles[-1].GetDirectory('exposure_blocks').GetListOfKeys():
            e_keys.append( e_key )
        for r_key in infiles[-1].GetDirectory('run_configs').GetListOfKeys():
            r_keys.append( r_key )
        for c_key in infiles[-1].GetDirectory('calibration_results').GetListOfKeys():
            c_keys.append( c_key )                        

    print '\tblocks:  {0}'.format( len(e_keys) )
    print '\tresults: {0}'.format( len(c_keys) )
    print '\tconfigs: {0}'.format( len(r_keys) )
    print '\twriting...',
    sys.stdout.flush()
    
    e_keys = sorted( e_keys, key=lambda k: k.GetName(), reverse=True )
    r_keys = sorted( r_keys, key=lambda k: k.GetName(), reverse=True )
    c_keys = sorted( c_keys, key=lambda k: k.GetName(), reverse=True )    

    for k, keys in enumerate( [ e_keys, r_keys, c_keys ] ):
        if k == 0:
            dir = 'exposure_blocks'
        if k == 1:
            dir = 'run_configs'
        if k == 2:
            dir = 'calibration_results'

        outfile = R.TFile( os.path.join( export_path, device ), 'update' )             
        outfile.cd(dir)
        t_arr = []
        count = 0
        tally = 0
        print
        print dir + ' i : n    ',
        for i_key, key in enumerate(keys):
            t_arr.append( key.ReadObj().CloneTree(-1,'fast') )
            tally += t_arr[-1].GetEntriesFast()
            if count >= 10000 or tally >= 10000:
                print '{} : {}    '.format(i_key,tally),
                sys.stdout.flush()
                count = 0
                tally = 0
                outfile.Write('',R.TObject.kOverwrite)
                outfile.Close()
                del t_arr
                t_arr = []
                outfile = R.TFile( os.path.join( export_path, device ), 'update' ) 
                outfile.cd(dir)
            count += 1
        print '{} : {}    '.format(i_key,tally),
        sys.stdout.flush()    
        outfile.Write('',R.TObject.kOverwrite)
        outfile.Close()
        del t_arr    
        
    for infile in infiles:
        infile.Close()
    print 'done'
