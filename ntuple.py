
from array import array as arr
import math             as math
import numpy            as np
import os               as os
import ROOT             as R
import sys              as sys

import macro

print '>> python ntuple.py [device list file] [output filename]'
print

device_list_file = sys.argv[1]
output_file      = sys.argv[2]

F = R.TFile( output_file, 'recreate' )

with open( device_list_file ) as f:
    for line in f.readlines():
        device = line.strip()
        
        macro.boilerplate.run(device)
        title = macro.boilerplate.out

        F.cd()
        t = R.TNtuple( device, title, 'year:time:L1:L1_pass:L1_skip:res_x:res_y:lat0:lon0:alt0:events:active_pixels:pixel_hits:max_val:int_val' )
        
        macro.rip_array.run(device)
        data = macro.rip_array.out
        for i in xrange( len(data['year']) ):
            t.Fill( data['year'][i],   data['time'][i],  data['L1'][i],   data['L1_pass'][i], data['L1_skip'][i], 
                    data['res_x'][i],  data['res_y'][i], data['lat0'][i], data['lon0'][i],    data['alt0'][i],
                    data['events'][i], data['active_pixels'][i], data['pixel_hits'][i], data['max_val'][i], data['int_val'][i]
                    )
        F.cd()
        t.Write()
F.Close()        
