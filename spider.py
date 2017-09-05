from array import array as array
import crayfis_data_pb2 as cray
import errno            as errno
import os               as os
import ROOT             as R
import sys              as sys
import tarfile          as tarf
import unpack           as unpack

if len(sys.argv) != 3:
    print '>> sausage: python spider.py import_path export_path'
    sys.exit()

    import_path = sys.argv[1]
    export_path = sys.argv[2]
    
tarfiles   = []
for path, directories, files in os.walk( import_path ):

        if '_old/' in path: continue
            # probably both good and bad data mixed together ultra low priority, 
            # about 24 files from < 2016, skip over..

        for filename in files:
            if filename.endswith('.tar.gz'):
                tarfiles.append( os.path.join(path,filename) )

tarfiles = sorted( tarfiles, key=lambda k: k.lower(), reverse=True )
for file in tarfiles:

    # search inside tar.gz files
    tarfile = tarf.open( file, 'r:gz' )
    messages = [ member for member in tarfile.getmembers() if member.name.endswith('.msg') ]
    for message in messages:
        msg  = tarfile.extractfile( message )
        print '{} / {}: '.format(file, message.name),
        basics = {}
        basics['tarfile'] = { 'value' : array('c', file + '->' + message.name + '\0'), 'code' : 'C' }
        unpack.CrayonMessage( msg, basics, export_path )
        msg.close()
        print ''
    tarfile.close()
