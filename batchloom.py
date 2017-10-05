import errno            as errno
import os               as os
import ROOT             as R
import sys              as sys
import tarfile          as tarf

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
    print device
    with tarf.open( os.path.join(export_path, device[:-4] + 'tar.gz'), 'w:gz' ) as tarfile:
        for path in paths:
            tarfile.add( os.path.join( path, device ) )
