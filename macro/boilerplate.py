"""
Makes string:  <Manufacturer> <Model> ( <1st Year> <1st Version> to <last Year> last Version> )

boilerplate.run(<device id>)
str = boilerplate.out
"""
from array import array as arr
import math             as math
import numpy            as np
import os               as os
import ROOT             as R
import sys              as sys

out = None

def run(device=''):
    global out
    
    D = R.gDirectory
    
    if device == '':
        print '>> sausage: boilerplate.run(<device id>)'
        print '>>          (returns title string as boilerplate.out)'
    
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

    out = '{:<8} {:<8} ({:4} {:^8}) to ({:4} {:^8})'.format( make[:8], model[:8], first_y, first_v[:8], last_y, last_v[:8] )
