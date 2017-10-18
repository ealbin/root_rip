"""

"""
from array import array as arr
import math             as math
import numpy            as np
import os               as os
import ROOT             as R
import sys              as sys

out = None

__pref__ = {}
__pref__['year'         ] = { 'logx' : 0, 'logy' : 1, 'xmin' :  2015.5, 'xmax' :    2018, 'nbin' :   251 }
__pref__['time'         ] = { 'logx' : 0, 'logy' : 1, 'xmin' :       0, 'xmax' :     179, 'nbin' :   180 }
__pref__['L1'           ] = { 'logx' : 0, 'logy' : 1, 'xmin' :     -.5, 'xmax' :   255.5, 'nbin' :   257 }
__pref__['L1_pass'      ] = { 'logx' : 1, 'logy' : 1, 'xmin' :       0, 'xmax' :       4, 'nbin' :   100 }
__pref__['L1_skip'      ] = { 'logx' : 1, 'logy' : 1, 'xmin' :       0, 'xmax' :       4, 'nbin' :   100 }
__pref__['res_x'        ] = { 'logx' : 0, 'logy' : 0, 'xmin' :       0, 'xmax' :    3000, 'nbin' :   101 }
__pref__['res_y'        ] = { 'logx' : 0, 'logy' : 0, 'xmin' :       0, 'xmax' :    3000, 'nbin' :   101 }
__pref__['lat0'         ] = { 'logx' : 0, 'logy' : 1, 'xmin' :  -89.95, 'xmax' :   90.05, 'nbin' :  1801 }
__pref__['lon0'         ] = { 'logx' : 0, 'logy' : 1, 'xmin' : -179.95, 'xmax' :  180.05, 'nbin' :  3601 }
__pref__['alt0'         ] = { 'logx' : 0, 'logy' : 1, 'xmin' :    -1.5, 'xmax' : 15000.5, 'nbin' : 15003 } 
__pref__['events'       ] = { 'logx' : 0, 'logy' : 1, 'xmin' :      .5, 'xmax' :  1000.5, 'nbin' :  1001 }
__pref__['active_pixels'] = { 'logx' : 0, 'logy' : 1, 'xmin' :      .5, 'xmax' : 10000.5, 'nbin' : 10001 }
__pref__['pixel_hits'   ] = { 'logx' : 0, 'logy' : 1, 'xmin' :      .5, 'xmax' : 10000.5, 'nbin' : 10001 }
__pref__['max_val'      ] = { 'logx' : 0, 'logy' : 1, 'xmin' :      .5, 'xmax' :   256.5, 'nbin' :   257 }
__pref__['int_val'      ] = { 'logx' : 1, 'logy' : 1, 'xmin' :       0, 'xmax' :       6, 'nbin' :   300 } 
# compositions
__pref__['L1_pass + L1_skip'       ] = { 'logx' : 1, 'logy' : 1, 'xmin' :       0, 'xmax' :      4, 'nbin' :   100 }
__pref__['L1_pass/time'            ] = { 'logx' : 0, 'logy' : 1, 'xmin' :      .5, 'xmax' :   70.5, 'nbin' :    71 }
__pref__['L1_skip/time'            ] = { 'logx' : 0, 'logy' : 1, 'xmin' :      .5, 'xmax' :   70.5, 'nbin' :    71 }
__pref__['(L1_pass+L1_skip)/time'  ] = { 'logx' : 0, 'logy' : 1, 'xmin' :      .5, 'xmax' :   70.5, 'nbin' :    71 }
__pref__['events/time'             ] = { 'logx' : 0, 'logy' : 1, 'xmin' :      .5, 'xmax' :   50.5, 'nbin' :    51 }
__pref__['active_pixels/time'      ] = { 'logx' : 0, 'logy' : 1, 'xmin' :      .5, 'xmax' : 1000.5, 'nbin' :  1001 }
__pref__['active_pixels/events'    ] = { 'logx' : 0, 'logy' : 1, 'xmin' :      .5, 'xmax' : 1000.5, 'nbin' :  1001 }
__pref__['pixel_hits/active_pixels'] = { 'logx' : 0, 'logy' : 1, 'xmin' :      .5, 'xmax' :  100.5, 'nbin' :   101 }
__pref__['int_val/time'            ] = { 'logx' : 1, 'logy' : 1, 'xmin' :       0, 'xmax' :      5, 'nbin' :   100 } 

def presets():
    global __pref__
    print  __pref__.keys()

def run(var, cuts='', reverse=True):
    global __pref__, out

    tokens = var.split(':')
    if not var in __pref__.keys():
        presets()

    F = R.TFile( '/home/ealbin/root_rip/analysis/ntuple.root', 'read' )
    D = R.gDirectory

    F.cd()
    keys = D.GetListOfKeys()

    logx = __pref__[var]['logx']
    xmin = __pref__[var]['xmin']
    xmax = __pref__[var]['xmax']
    nbin = __pref__[var]['nbin']
    harr = []
    for i, k in enumerate(keys):
        t = k.ReadObj()

        if logx == 0:
            bins = np.linspace( xmin, xmax, nbin )
        else:
            bins = np.logspace( xmin, xmax, nbin )

        name = '{}_{}'.format(i, k.GetName())
        h    = R.TH1D( name, '', nbin - 1, bins )
        t.Project( name, var, cuts )
        h.SetDirectory(0)
        harr.append(h)        
    harr.sort( key=lambda k: k.GetEntries(), reverse=reverse )

    out = R.THStack( 'stack', cuts )
    colors = [ R.kRed, R.kOrange, R.kYellow, R.kSpring, R.kGreen, R.kTeal, R.kCyan, R.kAzure, R.kBlue, R.kViolet, R.kMagenta, R.kPink ]
    for i, h in enumerate(harr):
        h.SetFillColor( colors[ i % len(colors) ] + int( i / len(colors) ) )
        h.SetLineColorAlpha( R.kBlack, 1. )
        out.Add(h)

    if __pref__[var]['logy'] == 1:
        out.SetMinimum(.9)
    else:
        out.SetMinimum(0.)
