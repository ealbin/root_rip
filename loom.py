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
    e_dir   = outfile.mkdir( 'exposure_blocks', 'exposure_blocks description' )
    r_dir   = outfile.mkdir( 'run_configs', 'run_configs description' )
    c_dir   = outfile.mkdir( 'calibration_results', 'calibration_results description' )

    tmpfile = R.TFile( os.path.join( export_path, '_tmp.root' ), 'recreate' )
    tmpfile.ReOpen('update')
    e_tmp   = tmpfile.mkdir( 'exposure_blocks', 'unsorted' )
    r_tmp   = tmpfile.mkdir( 'run_configs', 'unsorted' )
    c_tmp   = tmpfile.mkdir( 'calibration_results', 'unsorted' )

    for path in paths:
        print '\t' + path 
        infile = R.TFile( os.path.join( path, device ) ) 
        for dir in [ e_tmp, r_tmp, c_tmp ]:
            dir.cd()
            for key in infile.GetDirectory(dir.GetName()).GetListOfKeys():
                tree = key.ReadObj()
                clone = tree.CloneTree(-1,'fast')
                clone.Write('',R.TObject.kOverwrite)
                clone.SetDirectory(0)
                clone.Delete()
                tree.Delete()
        infile.Close()
        infile.Delete()
    tmpfile.Write('',R.TObject.kOverwrite)
    tmpfile.Close()
    tmpfile = R.TFile( os.path.join( export_path, '_tmp.root' ) )

    print '\tblocks:  {0}'.format( len(tmpfile.GetDirectory('exposure_blocks').GetListOfKeys()) )
    print '\tconfigs: {0}'.format( len(tmpfile.GetDirectory('run_configs').GetListOfKeys()) )
    print '\tresults: {0}'.format( len(tmpfile.GetDirectory('calibration_results').GetListOfKeys()) )
    print '\twriting...',
    sys.stdout.flush()

    for dir in [ e_dir, r_dir, c_dir ]:
        dir.cd()
        keys = [ key for key in tmpfile.GetDirectory(dir.GetName()).GetListOfKeys() ]
        keys = sorted( keys, key=lambda k: k.GetName(), reverse=False ) # most recent goes last
        dir_name = dir.GetName()
        for key in keys:
            tree = key.ReadObj()
            clone = tree.CloneTree(-1,'fast')
            clone.Write()
            clone.SetDirectory(0)
            clone.Delete()
            tree.Delete()
    outfile.Write('',R.TObject.kOverwrite)
    tmpfile.Close()
    outfile.Close()
    os.remove( os.path.join( export_path, '_tmp.root' ) )
    print 'done'
