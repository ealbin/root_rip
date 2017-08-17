import os   as os
import ROOT as R
import sys  as sys

if len(sys.argv) != 2:
    print '>> sausage:  python summary.py path'
    sys.exit()
start_path = sys.argv[1]
summary = []
for path, directories, files in os.walk( start_path ):
    for file in [ file for file in files if file.endswith('.root')]:
        f = R.TFile( os.path.join( path, file ) )
        d_blocks  = f.Get('exposure_blocks')
        d_configs = f.Get('run_configs')
        d_results = f.Get('calibration_results')

        n_blocks  = len( d_blocks.GetListOfKeys()  )
        n_configs = len( d_configs.GetListOfKeys() )
        n_results = len( d_results.GetListOfKeys() )

        if n_configs == 0:
            continue
        n_ok     = len([ key for key in d_configs.GetListOfKeys() if key.GetTitle().find('ok'     ) == 0 ])
        n_paired = len([ key for key in d_blocks.GetListOfKeys()  if key.GetTitle().find('config:') == 0 ])

        t = d_configs.Get( (d_configs.GetListOfKeys()[0]).GetName() )
        b = [ b.GetName() for b in t.GetListOfBranches() ]
        if not 'build_manufacturer' in b:
            summary.append( [ '', '', n_paired, n_blocks, n_ok, n_configs, n_results, file ] )
        else:
            t.GetEntry(0)
            make = t.build_manufacturer.lower().strip('\0')
            model = t.build_model.lower().strip('\0')
            summary.append( [ make, model, n_paired, n_blocks, n_ok, n_configs, n_results, file ] )
        f.Close()

summary = sorted( summary, key = lambda x: (x[0], x[2], x[3], x[4], x[5], x[7] ), reverse=False )
current = ''
print
print '{:>15}'.format('manufacturer'),
print ':',
print '{:<18}'.format('model'),
print '{:^20}'.format('exposure_blocks'),
print '{:^20}'.format('run_configs'),
print '{:^20}'.format('calibration_results'),
print '{:^30}'.format('filename')

print '{:>35}'.format(''),
print '{:^20}'.format('paired / all'),
print ' {:^22}'.format('ok / all'),
print '{:^18}'.format(''),
print '{:^33}'.format('(device_id)')
print '{:=^130}'.format('')
for s in summary:
    if s[0] != current:
        print
        print '{make:>15}:'.format(make=s[0]),
        current = s[0]
    else:
        print '{:>15} '.format(''),
    print '{model:<20}'.format(model=s[1]),
    print '{:^20}'.format( '{paired:>7} / {blocks:<7}'.format(paired=s[2],blocks=s[3]) ),
    print '{:^20}'.format( '{ok:>7} / {configs:<7}'.format(ok=s[4],configs=s[5]) ),
    print '{results:^20}  '.format(results=s[6] ),
    print '{file:^30} '.format(file=s[7])
