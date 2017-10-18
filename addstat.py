import numpy as np
import os    as os
import ROOT  as R
import sys   as sys

if len(sys.argv) != 2:
    print '>> sausage:  python addstat.py [device id]'
    sys.exit()

D = R.gDirectory
F = R.TFile( os.path.join('/home/ealbin/root_rip/data/' , sys.argv[1] + '.root'), 'read' )
f = R.TFile( os.path.join('/home/ealbin/root_rip/stats/', 'stats_' + sys.argv[1] + '.root' ), 'update' )

F.cd('exposure_blocks')
keys  = D.GetListOfKeys()
tkeys = [ key for key in keys if key.GetClassName() == 'TTree' and key.GetTitle().find('config:') == 0 ]

n_trees = len(tkeys)
print 'n_trees = {0}'.format(n_trees)
for itree, tkey in enumerate(tkeys):
    print 'adding stats to {0}, tree {1} of {2}'.format(tkey.GetName(),itree,n_trees)
    dirname = 'stats_' + tkey.GetName() 
    f.cd()
    d = D.GetKey( dirname )
    if d != None:
        t = tkey.ReadObj()
        branches = t.GetListOfBranches()
        n_events = t.GetEntries()
        t.GetEntry(0)
        L1_pass = t.L1_pass
        L1_skip = t.L1_skip
        max_val = 0
        int_val = 0
        for i in xrange( n_events ):
            t.GetEntry(i)
            int_val += sum(t.val)
            max_val  = max( [ max_val, max(t.val) ] )
        time = ( t.end_time - t.start_time ) / 1000.
        year = ( t.start_time / 1000. / 3600. / 24. / 365.24 ) + 1970.
        
        title = d.GetTitle().split(';')
        
        title.pop(3)
        title.insert(3, 'L1_pass={0}'.format(L1_pass))
        title.pop(4)
        title.insert(4, 'L1_skip={0}'.format(L1_skip))
        
#        title.insert( 1, 'L1_skip={0}'.format(L1_skip) )
#        title.insert( 1, 'L1_pass={0}'.format(L1_pass) )
#        title.insert( 0, 'time={0:.1f}'.format(time) )

#        title.insert(  0, 'year={0:.3f}'.format(year) )
#        title.insert( -1, 'max_val={0}'.format(max_val) )
#        title.insert( -1, 'int_val={0}'.format(int_val) )
        
        new = ''
        for token in title:
            new += token + ';'
        new.strip(';')
        d.SetTitle( new )
        t.Delete()

f.Close()
F.Close()
print 
print 'DONE'
