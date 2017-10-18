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
        print '>> sausage: python n_events.py [device id]'
        print '>>          (returns histogram)'
    
    F = R.TFile( '/home/ealbin/root_rip/data/{}.root'.format( device ), 'read' )
    
    F.cd('run_configs')
    keys = [ k for k in D.GetListOfKeys() if k.GetTitle().find('ok') == 0 ]
    
    first = keys[0].ReadObj()
    first.GetEntry(0)
    first_v = first.crayfis_build
    first_y = os.popen('date -d @{}'.format(first.start_time / 1000)).read().strip().split(' ')[-1]
    
    last  = keys[-1].ReadObj()
    last.GetEntry(0)
    last_v = last.crayfis_build
    last_y = os.popen('date -d @{}'.format(last.start_time / 1000)).read().strip().split(' ')[-1]
    
    make  = last.build_manufacturer
    model = last.build_model
    
    first.Delete()
    last.Delete()
    
    F.cd('exposure_blocks')
    
    keys = [ k for k in D.GetListOfKeys() if k.GetTitle().find('config') == 0 ]
    l    = len(keys)
    
    title = '{:^5} {:^5} ({:^4} {:^5}) to ({:^4} {:^5})'.format( make[:5], model[:5], first_y, first_v[:5], last_y, last_v[:5] )
    title += ';Number of Events / Exposure Block;Occurances to Date'
    h = R.TH1I( device, title, 1000, -.5, 999.5 )
    h.SetDirectory(0)
        
    for k in keys:
        tmp = k.ReadObj()
        h.Fill( tmp.GetEntriesFast() )
        tmp.Delete()
    F.Close()
    F.Delete()
    
    
