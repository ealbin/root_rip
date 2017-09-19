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

stopwatch = R.TStopwatch()
stopwatch.Start()

tarfiles   = []
for path, directories, files in os.walk( import_path ):

        if '_old/' in path: continue
            # probably both good and bad data mixed together ultra low priority, 
            # about 24 files from < 2016, skip over..

        for filename in files:
            if filename.endswith('.tar.gz'):
                tarfiles.append( os.path.join(path[path.find('/data'):],filename) )

tarfiles = sorted( tarfiles, key=lambda k: k.lower(), reverse=True )
n_messages = 0
for file in tarfiles:

    # search inside tar.gz files
    print
    basepath = import_path[:import_path.find('/data')]
    tarfile = tarf.open( basepath + file, 'r:gz' )
    messages = sorted( [ member for member in tarfile.getmembers() if member.name.endswith('.msg') ], key=lambda k: k.name.lower() )
    for message in messages:
        n_messages += 1
        msg  = tarfile.extractfile( message )
        print '{A} / {B}: '.format(A=file, B=message.name),
        basics = {}
        basics['tarfile'] = { 'value' : array('c', file + '->' + message.name + '\0'), 'code' : 'C' }
        unpack.CrayonMessage( msg, basics, export_path )
        msg.close()
        print ''
        sys.stdout.flush()
    tarfile.close()
    print
    sofar = stopwatch.CpuTime()
    stopwatch.Continue()
    print 'CPU TIME ELAPSE: {0}, over {1} messages = {2} [s/message]'.format(sofar, n_messages, sofar / float(n_messages) )
