import numpy as np
import os    as os
import ROOT  as R
import sys   as sys

if len(sys.argv) != 3 and len(sys.argv) != 4:
    print '>> sausage:  python probe.py file.root output_dir [-v|--verbose]'
    sys.exit()

print 'loading {0}'.format(sys.argv[1])
_verbose = False
if len(sys.argv) == 4:
    if sys.argv[3] == '-v' or sys.argv[3] == '--verbose':
        _verbose = True
#os.system( 'cp {} {}'.format( sys.arg[1], sys.arg[2] ) )
F = R.TFile( sys.argv[1], 'read' )
out = os.path.join( sys.argv[2], 'stats_' + os.path.basename(sys.argv[1]) )
if os.path.exists(out):
    f = R.TFile( out, 'update' )
else:    
    f = R.TFile( out, 'create' )
D = R.gDirectory

F.cd('exposure_blocks')
keys  = D.GetListOfKeys()
tkeys = [ key for key in keys if key.GetClassName() == 'TTree' ]
dkeys = [ key for key in keys if key.GetClassName() == 'TDirectoryFile' ]

n_trees = len(tkeys)
print 'n_trees = {0}'.format(n_trees)
for itree, tkey in enumerate(tkeys):
    print 'probing {0}, tree {1} of {2}'.format(tkey.GetName(),itree,n_trees)
    dirname = 'stats_' + tkey.GetName() 
    if tkey.GetTitle().find('config:') == 0:
        f.cd()
        if D.Get( dirname ) != None:
            print '\texisting stats, skipping'
            continue
        t = tkey.ReadObj()
        branches = t.GetListOfBranches()
        t.GetEntry(0)
        res_x  = t.res_x
        res_y  = t.res_y
        thresh = t.L1_thresh
        lat = -1
        lon = -1
        alt = -1
        if 'gps_lat' in branches:
            lat = t.gps_lat
            lon = t.gps_lon
        if 'gps_alt' in branches:
            alt = t.gps_alt
        if _verbose:
            print '\tmkdir {0}'.format(dirname)
        D.mkdir( dirname, 'L1={0};res={1},{2};lat0={3};lon0={4};alt0={5};events=0;active_pixels=0;pixel_hits=0'.format(thresh,res_x,res_y,lat,lon,alt) )
        D.cd(dirname)
        hists = np.zeros( res_x * res_y + res_x, dtype=R.TH1I )
        entries = t.GetEntries()
        if _verbose:
            print '\tt entries: {0}'.format(entries)
        for entry in xrange( entries ):
            t.GetEntry(entry)
            l = len(t.val)
            for i in xrange(l):
                x = t.x[i]
                y = t.y[i]
                v = t.val[i]
                j = res_x * y + x
                if hists[j] == 0:
                    hists[j] = R.TH1I( 'pixel_x{0}_y{1}:res_{2}_by_{3}'.format(x,y,res_x,res_y), '(x,y) = ({0},{1});Pixel Value;Counts'.format(x,y), 255, 0, 255 )
                    hists[j].SetStats(0)
                    hists[j].SetDirectory(0)
                hists[ res_x * y + x ].Fill(v)                

        h_entries = 0
        n_hists   = 0
        if _verbose:
            print '\th entries:',
        for hist in hists:
            if hist == 0:
                continue
            if hist.GetEntries() > 0:
                n_hists += 1
                h_entries += int(hist.GetEntries())
                if _verbose:
                    print '{0} +'.format(int(hist.GetEntries())),
                hist.Write('', R.TObject.kOverwrite)
                tokens = hist.GetName().split(':')[0].split('_')
                x = tokens[1].split('x')[1]
                y = tokens[2].split('y')[1]
                D.GetKey( hist.GetName() ).SetTitle( 'x={0};y={1};n_entries={2}'.format(x,y,int(hist.GetEntries())) )
        if _verbose:
            print '\b\b\b',
            print '= {0}'.format(h_entries)
        f.cd()
        D.GetKey(dirname).SetTitle( 'L1={0};res={1},{2};lat0={3:.2f};lon0={4:.2f};alt0={5};events={6};active_pixels={7};pixel_hits={8}'.format(thresh,res_x,res_y,lat,lon,alt,entries,n_hists,h_entries) )
        t.Delete()
        for hist in hists:
            if hist == 0:
                continue
            hist.Delete()
    else:
        print '\tno paired run_config, skipping'
        # remove non-paired with run_config dirs
        if D.Get( dirname ) != None:
            print '\tdeleting non-paired directory {0}'.format(dirname)
            D.rmdir( dirname )
f.Close()
F.Close()
print 
print 'DONE'
