# takes about 50ms to open/read tarfile
# takes about 10 to 100ms to process a message
# finding: around 100 ms to process a message

# most often there are 500 messages/tarfile
# 1000 on average and upto around 2000
# finding:  around 1000 messages/tarfile
# finding:  around 35,500 tarfiles

# maths:  35500 [tarfiles] * 1000 [msg/tarfile] * 100 [ms/msg] = 41 days

from array import array as array
import crayfis_data_pb2 as cray
import unpack as unpack

import ROOT as R
import tarfile as tarf
import os as os
import sys as sys

stopwatch = R.TBenchmark()
stopwatch.Start("stopwatch")

tarfiles = []
for path, directories, files in os.walk( '/data/daq.crayfis.io/raw/' ):

    if '_old/' in path: continue
    
    for filename in files:
        if filename.endswith('.tar.gz'):
            tarfiles.append( os.path.join(path,filename) )
tarfiles = sorted( tarfiles, key=lambda k: k.lower(), reverse=True )
print len(tarfiles)
os.exit()
stopwatch.Show("stopwatch")

timing = R.TH1D( "timing", "timing;time;counts", 10000, 0, 10000 )
C = R.TCanvas("bigC", "bigC", 600, 600)
C.SetLogy()
update = 0
print
ntarfiles = len(tarfiles)
for ifile, file in enumerate(tarfiles):
    tarfile = tarf.open( file, 'r:gz' )
    tarsize = os.path.getsize(file)
    messages = [ member for member in tarfile.getmembers() if member.name.endswith('.msg') ]
    nmessages = len(messages)
    print ' ave: ' + str( tarsize / float(nmessages) ) + ' bytes/message'
    stopwatch.Reset()
    stopwatch.Start("stopwatch")
    timing.Fill( len(messages) )
#    for message in messages:
#        msg = tarfile.extractfile( message )
#        basics = {}
#        basics['tarfile'] = { 'value' : array('c', file + '->' + message.name + '\0'),'code':'C'}
#        print file + '->' + message.name
#        unpack.CrayonMessage( msg,basics,'/home/ealbin/root_rip/timing/')
#        msg.close()
#    stopwatch.Stop("stopwatch")
#    timing.Fill( stopwatch.GetCpuTime("stopwatch")/float(len(messages)) )
    if update == 5:
        print "\r                                              \r",
        print "Working... {:>.3}%\r".format( ifile / float(ntarfiles) * 100. ),
        sys.stdout.flush()
        timing.Draw()
        C.Update()
        update = -1
    update += 1
timing.Draw()
C.Update()
print
