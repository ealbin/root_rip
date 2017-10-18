"""
instant 1-D histogram
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
            continue
        else:
            a = [ 0 for x in xrange(len(data)) ]
            for i, d in enumerate(data):
                start = d.find(header)
                end   = d.find(';', start)
                start += len( header + '=' )
                a[i]  = float( d[ start : end ] )

            if header == 'time':
                R.gStyle.SetOptStat('nemruo')
                out[header] = R.TH1D( device + '_' + header, title + ';seconds;counts', 180, -.5, 179.5 )
                out[header].UseCurrentStyle()
                out[header].SetDirectory(0)
                for ai in a:
                    out[header].Fill(ai)
            elif header == 'L1_skip':
                R.gStyle.SetOptStat('nemruo')
                out[header] = R.TH1D( device + '_' + header, title + ';L1_skips;counts', 400, -.5, 39999.5 )
                out[header].UseCurrentStyle()                
                out[header].SetDirectory(0)
                for ai in a:
                    out[header].Fill(ai)
            else:
                TH1.fill(a)
                out[header] = TH1.out.Clone()
                out[header].SetTitle(title)
                out[header].SetDirectory(0)

    # extra plots
    header = 'frame_rate'
    a = [ 0 for x in xrange(len(data)) ]
    for i, d in enumerate(data):
        start = d.find(header)
        end   = d.find(';', start)
        start += len( header + '=' )
        a[i]  = float( d[ start : end ] )

    if header == 'time':
        R.gStyle.SetOptStat('nemruo')
        out[header] = R.TH1D( device + '_' + header, title + ';seconds;counts', 180, -.5, 179.5 )
        out[header].UseCurrentStyle()
        out[header].SetDirectory(0)
        for ai in a:
            out[header].Fill(ai)
