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

        d_blocks  = f.GetDirectory('exposure_blocks')
        d_configs = f.GetDirectory('run_configs')
        d_results = f.GetDirectory('calibration_results')

        n_blocks  = len( d_blocks.GetListOfKeys()  )
        n_configs = len( d_configs.GetListOfKeys() )
        n_results = len( d_results.GetListOfKeys() )
        
#        if f.GetStreamerInfoList() == None:
#            print os.popen('ls -hs {}'.format( os.path.join(path,file) ) ).read().strip()
#            print os.popen('egrep {} /home/ealbin/root_rip/compared'.format( file.strip('.root') )).read().strip()
#            f.ls()
#            d_blocks.ls()
#            d_configs.ls()
#            d_results.ls()
#            print
#            sys.stdout.flush()
#            continue
            
        if n_configs == 0:
            continue
        n_ok     = len([ key for key in d_configs.GetListOfKeys() if key.GetTitle().find('ok'     ) == 0 ])
        n_paired = len([ key for key in d_blocks.GetListOfKeys()  if key.GetTitle().find('config:') == 0 ])

        t0 = d_configs.Get( (d_configs.GetListOfKeys()[ 0]).GetName() )
        t1 = d_configs.Get( (d_configs.GetListOfKeys()[-1]).GetName() )
        b0 = [ b.GetName() for b in t0.GetListOfBranches() ]
        b1 = [ b.GetName() for b in t1.GetListOfBranches() ]

        t0.GetEntry(0)
        if ( not 'build_manufacturer' in b0 ):
            make0  = 'unknown'
            model0 = 'unknown'
        else:
            make0    = t0.build_manufacturer.lower().strip('\0')
            model0   = t0.build_model.lower().strip('\0')
        version0 = t0.crayfis_build.lower().strip('\0')
        start_time = int(t0.start_time)
        
        t1.GetEntry(0)
        if ( not 'build_manufacturer' in b1 ):
            make1  = 'unknown'
            model1 = 'unknown'
        else:
            make1    = t1.build_manufacturer.lower().strip('\0')
            model1   = t1.build_model.lower().strip('\0')
        version1 = t1.crayfis_build.lower().strip('\0')            
        last_time = int(t1.submit_time)
        make = make0
        if ( make0 != make1 ):
            make = 'various'
        model = model0
        if ( model0 != model1 ):
            model = 'various'

        dt     = float(last_time - start_time/1000.) / 3600. / 24.
        date0  = os.popen('date -d @{}'.format( float(start_time)/1000. ) ).read().strip().split(' ')
        date1  = os.popen('date -d @{}'.format( float(last_time)        ) ).read().strip().split(' ')
        year0  = date0[-1]
        year1  = date1[-1]
        month0 = date0[1]
        month1 = date1[1]

        summary.append( [ make, model, n_paired, n_blocks, n_ok, n_configs, n_results, file, year0, month0, version0, year1, month1, version1, dt ] )
        f.Close()

summary = sorted( summary, key = lambda x: (x[0], x[2], x[3], x[4], x[5], x[7] ), reverse=False )
current = ''
print
print '{:>15}'.format('manufacturer'),
print ':',
print '{:<18}'.format('model'),
print '{:^20}'.format('exposure_blocks'),
print '{:^20}'.format('run_configs'),
print '{:^18}'.format('calibration_results'),
print '{:^28}'.format('filename'),
print '{:^36}'.format('start/end dates, versions and days active')

print '{:>35}'.format(''),
print '{:^20}'.format('paired / all'),
print ' {:^22}'.format('ok / all'),
print '{:^18}'.format(''),
print '{:^30}'.format('(device_id)')
print '{:=^180}'.format('')
for s in summary:
    if s[0] != current:
        print
#        print '{make:>15}:'.format(make=s[0]),
        current = s[0]
#    else:
#        print '{:>15} '.format(''),
    print '{make:>15}:'.format(make=s[0][:15]),
    
    print '{model:<20}'.format(model=s[1][:20]),
    print '{:^20}'.format( '{paired:>7} / {blocks:<7}'.format(paired=s[2],blocks=s[3]) ),
    print '{:^20}'.format( '{ok:>7} / {configs:<7}'.format(ok=s[4],configs=s[5]) ),
    print '{results:^16}  '.format(results=s[6] ),
    print '{file:^25}'.format(file=s[7]),
    print '{year0:4} {month0:3} ({version0:<10}) to {year1:4} {month1:3} ({version1:<10}) [{days:>4.0f}]'.format(year0=s[8],month0=s[9],version0=s[10][:10],year1=s[11],month1=s[12],version1=s[13][:10],days=s[14])
