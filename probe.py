import numpy as np
import ROOT  as R
import sys   as sys

if len(sys.argv) != 2:
    print '>> sausage:  python probe.py file.root'
    sys.exit()

print 'loading {}'.format(sys.argv[1])
f = R.TFile( sys.argv[1], 'update' )
d = R.gDirectory
d.cd('exposure_blocks')

keys  = d.GetListOfKeys()
trees = [ key for key in keys if key.GetClassName() == 'TTree' ]
dirs  = [ key for key in keys if key.GetClassName() == 'TDirectoryFile' ]

n_trees = len(trees)
print 'n_trees = {}'.format(n_trees)
for i_tree, tree in enumerate(trees):
    print 'probing {}, tree {} of {}'.format(tree.GetName(),i_tree,n_trees)
    dirname = 'stats_' + tree.GetName() 
    if tree.GetTitle().find('config:') == 0:
        if d.Get( dirname ) != None:
            print '\texisting stats, skipping'
            continue
        t = tree.ReadObj()
        t.GetEntry(0)
        res_x = t.res_x
        res_y = t.res_y
        print '\tmkdir {}'.format(dirname)
        d.mkdir( dirname, 'res={},{};n_hists=0;n_entries=0'.format(res_x,res_y) )
        d.cd(dirname)
        hists = np.zeros( res_x * res_y + res_x, dtype=R.TH1I )
        entries = t.GetEntries()
        print '\tt entries: {}'.format(entries)
        for entry in xrange( entries ):
            t.GetEntry(entry)
            for i in xrange(len(t.val)):
                x = t.x[i]
                y = t.y[i]
                v = t.val[i]
                j = res_x * y + x
                if hists[j] == 0:
                    hists[j] = R.TH1I( 'pixel_x{}_y{}:{}_by_{}'.format(x,y,res_x,res_y), '(x,y) = ({},{});Pixel Value;Counts'.format(x,y), 255, 0, 255 )
                    hists[j].SetStats(0)
                    hists[j].SetDirectory(0)
                hists[ res_x * y + x ].Fill(v)                

        h_entries = 0
        n_hists   = 0
        print '\th entries:',
        for hist in hists:
            if hist == 0:
                continue
            if hist.GetEntries() > 0:
                n_hists += 1
                h_entries += int(hist.GetEntries())
                print '{} +'.format(int(hist.GetEntries())),
                hist.Write('', R.TObject.kOverwrite)
                tokens = hist.GetName().split(':')[0].split('_')
                x = tokens[1].split('x')[1]
                y = tokens[2].split('y')[1]
                d.GetKey( hist.GetName() ).SetTitle( 'x={};y={};n_entries={}'.format(x,y,int(hist.GetEntries())) )
        print '\b\b\b',
        print '= {}'.format(h_entries)
        d.SetTitle( 'res={},{};n_hists={};n_entries={}'.format(res_x,res_y,n_hists,h_entries) )
        d.cd('..')
        d.GetKey(dirname).SetTitle( 'res={},{};n_hists={};n_entries={}'.format(res_x,res_y,n_hists,h_entries) )
        t.Delete()

    else:
        print '\tno paired run_config, skipping'
        # remove non-paired with run_config dirs
        if R.gDirectory.Get( dirname ) != None:
            print '\tdeleting non-paired directory {}'.format(dirname)
            R.gDirectory.rmdir( dirname )
f.Close()
print 
print 'DONE'