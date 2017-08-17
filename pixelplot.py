import ROOT as R
import sys
import numpy as np

if len(sys.argv) == 1:
    print '>> sausage: python pixelplot.py filename.root'
    
F = R.TFile( sys.argv[1] )
D = R.gDirectory
D.cd('exposure_blocks')

dirs = [ key.GetName() for key in D.GetListOfKeys() if key.GetClassName() == 'TDirectoryFile' ]
res_x = None
res_y = None
hists = [None]
ndirs = len(dirs)
target = 0
print '     ',
for i,dir in enumerate(dirs):
    if i / float(ndirs) > target / 100.:
        print '\b\b\b\b\b\b',
        print '{:3}%'.format(target),
        sys.stdout.flush()
        target += 1
    D.cd(dir)
    histkeys = [ key for key in D.GetListOfKeys() if key.GetClassName() == 'TH1I' ]
    for histkey in histkeys:
        h = D.Get( histkey.GetName() )

        if res_x == None:
            res_x = int( histkey.GetName().split(':')[1].split('_')[0] )
        if res_y == None:
            res_y = int( histkey.GetName().split(':')[1].split('_')[-1] )
        if len(hists) == 1 and res_x != None and res_y != None:
            hists = np.zeros( res_x * res_y + res_x, dtype=R.TH1I )

        x = int( histkey.GetTitle().split(';')[0].split('=')[1] )
        y = int( histkey.GetTitle().split(';')[1].split('=')[1] )        

        if len(hists) > 1:
            if hists[ res_x * y + x ] == 0:
                hists[ res_x * y + x ] = h.Clone()
            else:
                hists[ res_x * y + x ].Add( h )
        h.Delete()
    D.cd('../')
    
fout = R.TFile( 'plot.root', 'recreate' )
entries = 0
for hist in hists:
    if hist != 0:
        hist.SetTitle('')
        hist.SetDirectory(0)
        hist.SetStats(0)
        hist.Write()
        entries += hist.GetEntries()
print entries
fout.Close()
