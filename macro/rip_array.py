"""

"""
from array import array as arr
import math             as math
import numpy            as np
import os               as os
import ROOT             as R
import sys              as sys

import boilerplate
import TH1

out = {}

def run(device):
    global out

    boilerplate.run(device)
    title = boilerplate.out

    F = R.TFile( os.path.join( '/home/ealbin/root_rip/stats/', 'stats_' + device + '.root' ), 'read' )
    D = R.gDirectory
    
    data    = [ d.GetTitle() for d in D.GetListOfKeys() ]
    headers = [ t.strip('0123456789.,-') for t in data[0].split(';') ]
    headers = [ t.strip('=') for t in headers ]
    headers = [ t for t in headers if len(t) > 0 ]

    for header in headers:

        if   header == 'res':
            a = [ [0,0] for x in xrange(len(data)) ]
            for i, d in enumerate(data):
                start = d.find(header)
                end   = d.find(';', start)
                comma = d.find(',', start)
                start += len( header + '=' )
                a[i]  = [ float( d[ start : comma ] ), float( d[ comma + 1 : end ] ) ]
            out['res_x'] = [ x[0] for x in a ]
            out['res_y'] = [ x[1] for x in a ]
        else:
            a = [ 0 for x in xrange(len(data)) ]
            for i, d in enumerate(data):
                start = d.find(header)
                end   = d.find(';', start)
                start += len( header + '=' )
                a[i]  = float( d[ start : end ] )
            out[header] = a
