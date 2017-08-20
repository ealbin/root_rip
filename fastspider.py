# takes about 50ms to open/read tarfile

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
stopwatch.Show("stopwatch")

timing = R.TH1D( "timing", "timing;time;counts", 100, 0, .2 )
C = R.TCanvas("bigC", "bigC", 600, 600)
C.SetLogy()
update = 0
print
ntarfiles = len(tarfiles)
for ifile, file in enumerate(tarfiles):
    stopwatch.Reset()
    stopwatch.Start("stopwatch")
    tarfile = tarf.open( file, 'r:gz' )
    messages = [ member for member in tarfile.getmembers() if member.name.endswith('.msg') ]
    for message in messages:
        msg = tarfile.extractfile( message )
    stopwatch.Stop("stopwatch")
    timing.Fill( stopwatch.GetCpuTime("stopwatch") )
    if update == 100:
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
