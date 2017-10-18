from array import array as arr
import math             as math
import numpy            as np
import os               as os
import ROOT             as R
import sys              as sys

h = None

def run(device=''):
    global h
    
    D = R.gDirectory
    
    if device == '':
        print '>> sausage: python hits_per_pix_per_event.py [device id]'
        print '>>          (returns histogram)'
    
    F = R.TFile( '/home/ealbin/root_rip/data/{}.root'.format(device), 'read' )
    F.cd('run_configs')
    keys = [ k for k in D.GetListOfKeys() if k.GetTitle().find('ok') == 0 ]
    
    first = keys[0].ReadObj()
    first.GetEntry(0)
    first_v = first.crayfis_build.strip('\0')
    first_y = os.popen('date -d @{}'.format(first.start_time / 1000)).read().strip().split(' ')[-1]
    
    last  = keys[-1].ReadObj()
    last.GetEntry(0)
    last_v = last.crayfis_build.strip('\0')
    last_y = os.popen('date -d @{}'.format(last.start_time / 1000)).read().strip().split(' ')[-1]
    
    make  = last.build_manufacturer.strip('\0')
    model = last.build_model.strip('\0')
    
    first.Delete()
    last.Delete()
    F.Close()
    F.Delete()

    F = R.TFile( '/home/ealbin/root_rip/stats/stats_{}.root'.format( device ), 'read' )    
    
    keys = [ k for k in D.GetListOfKeys() ]
    l    = len(keys)
    
    title = '{:^8} {:^8} ({:^4} {:^8}) to ({:^4} {:^8})'.format( make[:8], model[:8], first_y, first_v[:8], last_y, last_v[:8] )
    title += ';Average Hits per Pixel per Event;Occurances to Date'
    R.gStyle.SetOptStat('nemruo')
    h = R.TH1D( device, title, 150, -.5, 1.45 )
    h.SetDirectory(0)
        
    for k in keys:
        info = k.GetTitle().split(';')
        events = int(info[5].strip('events='))
        pixels = int(info[6].strip('active_pixels='))
        hits   = int(info[7].strip('pixel_hits='))
        if pixels == 0 or events == 0:
            continue
        h.Fill( float(hits) / float(pixels) / float(events) )
    F.Close()
    F.Delete()
    
    
