"""
instant 1-D histogram
"""
from array import array as arr
import math             as math
import numpy            as np
import os               as os
import ROOT             as R
import sys              as sys

out = None

__h_num__ = 0

def fill(data):
    global out, __h_num__

    if out != None:
        out.Delete()
            
    R.gStyle.SetOptStat('nemruo')

    minimum = min(data)
    maximum = max(data)
    length  = len(data)
    
    if minimum < 0.:
        low  = 2*int(minimum) - 1.5
        high = .5
    else:
        low  = -.5
        high = 2*int(maximum) + 1.5

    if maximum == minimum:
        bins = 1
    else:
        bins  = max( [ 1, int(length / math.sqrt(length)) ] )
        bins *= int( ( high - low ) / ( maximum - minimum ) )
    bins = max( 1, bins )
    
    width = ( high - low ) / float(bins)
    width = float( '{:.1g}'.format(width) ) # round to 2 sigs
    high  = low + width * bins
    
    out    = R.TH1D( 'th1d_'+str(__h_num__), '', bins, low, high )
    out.SetDirectory(0)
    offset = out.GetBinCenter( out.FindBin(0.) )
    low   -= offset
    high  -= offset

    out.Delete()
    out = R.TH1D( 'th1d_'+str(__h_num__), '', bins, low, high )
    out.SetDirectory(0)
    
    for d in data:
        out.Fill(d)

    __h_num__ += 1
