import math
import numpy as np
import ROOT as R
import sys

if len(sys.argv) == 1:
    print '>> sausage: python morestats.py filename.root'
    sys.exit()
    
D = R.gDirectory
F = R.TFile( sys.argv[1], 'update' )

D.cd('exposure_blocks')
b_keys = [ key for key in D.GetListOfKeys() if key.GetClassName() == 'TDirectoryFile' ]

for i, d_key in enumerate(b_keys):

    if int( d_key.GetTitle().split(';')[2].split('=')[1] ) < 2:
        continue

    D.cd(d_key.GetName())
    h_keys = [ key.GetTitle() for key in D.GetListOfKeys() ]
    meta   = [ key.split(';') for key in h_keys ]

    x = [ int(m[0].split('=')[1]) for m in meta ]
    y = [ int(m[1].split('=')[1]) for m in meta ]
    n = [ int(m[2].split('=')[1]) for m in meta ]

    d = []
    for i in xrange(len(x)):
        for j in xrange(i+1, len(x)):
            for k in xrange(n[i] * n[j]):
                d.append( math.sqrt((x[j] - x[i])**2 + (y[j] - y[i])**2) )
    if len(d) > 0:
        mean   = np.mean(d)
        median = np.median(d)
        std    = np.std(d)
        old_title = ''.join( token + ';' for token in d_key.GetTitle().split(';')[:3] )[:-1]
        new_title = old_title + ';d_mean={:.4};d_median={:.4};d_std={:.4}'.format(mean,median,std) 
        d_key.SetTitle(new_title)
    D.cd('..')
F.Close()
