import os   as os
import ROOT as R
import sys  as sys

if len(sys.argv) == 1:
    print '>> usage:  python qualitycontrol.py [device_id].root'
    sys.exit()

f = R.TFile( sys.argv[1], 'update' )
d = R.gDirectory
d_blocks  = d.Get('exposure_blocks')
d_configs = d.Get('run_configs')
d_results = d.Get('calibration_results')

n_blocks  = len( d_blocks.GetListOfKeys()  )
n_configs = len( d_configs.GetListOfKeys() )
n_results = len( d_results.GetListOfKeys() )

print sys.argv[1]
if n_configs == 0:
    print '>> no run_configs'
    sys.exit()
print

block_keys   = sorted( [ key.GetName() for key in d_blocks.GetListOfKeys()  ] )
config_keys  = sorted( [ key.GetName() for key in d_configs.GetListOfKeys() ] )
results_keys = sorted( [ key.GetName() for key in d_results.GetListOfKeys() ] )

# validate run_configs, then exposure_blocks

# Valid RunConfig
d.cd('run_configs')
print '>\t run_configs:'
for ckey in config_keys:
    title = d_configs.GetKey(ckey).GetTitle()
    print '\t\trun_config: {0}'.format(d_configs.GetKey(ckey).GetName())
    if title.find('ignored:') >= 0:
        print '\t\t - skipping b/c ignored'
        continue
    if title.find('ok:') >= 0:
        print '\t\t - skipping b/c already certified OK'
        continue

    tree = d_configs.Get(ckey)

    if tree.GetEntries() != 1:
        print '\t\t - n_entries != 1, flagging tree and moving on'
        d_configs.GetKey(ckey).SetTitle('ignored: n_entries != 1')
        tree.Delete()
        continue

    tree.GetEntry(0)
    branches = [ branch.GetName() for branch in tree.GetListOfBranches() ]

    if ( not 'build_manufacturer' in branches or
         not 'build_model'        in branches  ):
        print '\t\t - essential variables missing, flagging and moving on'
        d_configs.GetKey(ckey).SetTitle('ignored: build_{manufacturer/model} not found')
        tree.Delete()
        continue

    crayfis_build = tree.crayfis_build.lower().strip('\0')
    if ( crayfis_build != 'v0.5.0'     and
         crayfis_build != 'v0.5.1'     and
         crayfis_build != 'v0.6.0-rc0' and
         crayfis_build != 'v0.7.0'     and
         crayfis_build != 'v0.8.1'      ):
        print '\t\t - crayfis_build version not ok, flagging and moving on'
        d_configs.GetKey(ckey).SetTitle('ignored: ' + crayfis_build)
        tree.Delete()
        continue

    d_configs.GetKey(ckey).SetTitle('ok')
    tree.Delete()

# Valid ExposureBlock
print
print '>\texposure_blocks:'
d.cd('../exposure_blocks')
for bkey in block_keys:
    title = d_blocks.GetKey(bkey).GetTitle()
    print '\t\texposure_block: {0}'.format(d_blocks.GetKey(bkey).GetName())
    if title.find('ignored:') >= 0: # skip already flagged
        print '\t\t - skipping b/c ignored'
        continue
    if title.find('config:') >= 0: # skip already done
        print '\t\t - skipping b/c already paired to run_config'
        continue

    tree = d_blocks.Get(bkey)

    if tree.GetEntries() == 0:
        print '\t\t - n_entries = 0, flagging tree and moving on'
        d_blocks.GetKey(bkey).SetTitle('ignored: n_entries == 0')
        tree.Delete()
        continue

    start_time = bkey

    # locate appropriate run_config file to pair
    last = config_keys[0]
    diff = int(start_time) - int(last)
    if diff > 0:
        best = diff
        for i, ckey in enumerate(config_keys):
            diff = int(start_time) - int(ckey)
            if diff > best or diff < 0:
                break
            best = diff
            last = ckey
    if d_configs.GetKey(last).GetTitle() != 'ok':
        print '\t\t - run_config is bad or missing, flagging tree and moving on'
        d_blocks.GetKey(bkey).SetTitle('ignored: bad or missing run_config')
        tree.Delete()
        continue
        
    d_blocks.GetKey(bkey).SetTitle('config:' + last)
    tree.Delete()
    
f.Close()
print 'DONE'
