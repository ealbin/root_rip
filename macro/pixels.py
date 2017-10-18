"""
pixel value histogram array
"""
from array import array as arr
import math             as math
import numpy            as np
import os               as os
import ROOT             as R
import sys              as sys

import boilerplate

out = None
id  = None

def run(device=''):
    global out, id
    
    D = R.gDirectory
    
    if device == '':
        print '>> sausage: pixels.run(<device id>)'
        print '>>          (returns pixel value histogram array)'
    id = device
        
    F = R.TFile( '/home/ealbin/root_rip/stats/stats_{}.root'.format(id), 'read' )    
    
    keys = [ k for k in D.GetListOfKeys() ]
    l    = len(keys)
    
    boilerplate.run(id)
    title  = boilerplate.out
    title += ';Pixel Value;Counts'
    R.gStyle.SetOptStat('ne')

    out = {}
    for k in keys:
        subkeys = k.ReadObj().GetListOfKeys()
        for sk in subkeys:
            hist = sk.ReadObj()
            hist.SetDirectory(0)
            name = hist.GetName()
            if name in out.keys():
                out[name].Add(hist)
                hist.Delete()
            else:
                out[name] = hist

    F.Close()
    F.Delete()

def sort():
    global out

    if out == None:
        print ' >> run pixels.run(<device id>) first'
        return

    out = sorted( out.values(), key=lambda k: k.GetEntries() )

    out = [ [ o, o.GetEntries(), o.GetMaximum(), o.GetMaximumBin() ] for o in out ]

def plot():    
    global out
    
    if out == None or type(out) == dict:
        print ' >> run pixels.run(<device id>) first'
        print '    then pixels.sort()'
        return

    boilerplate.run(id)
    title  = boilerplate.out
    etitle = title + ';Hits per Pixel;Counts'
    mtitle = title + ';Mean hit value per Pixel;Std Dev hit value'
                
    he = R.TH1I( 'he', etitle, 200, -.5, 199.5 )
    hm = R.TH2D( 'hm', mtitle, 256, -.5, 255.5, 100, -.5, 99.5 )
    for h in out:
        he.Fill( h.GetEntries() )
        hm.Fill( h.GetMean(), h.GetStdDev() )
        
    return [ he, hm ]        
        
