# finding: around 100 ms to process a message
# finding: around 1000 messages/tarfile
# finding: around 35,500 tarfiles
# estimate:  35500 [tarfiles] * 1000 [msg/tarfile] * 100 [ms/msg] = 41 days (aka 1000 cpu hrs)
#            1 [hr] * 3600 [s/hr] * 1000 [ms/s] / 100 [ms/msg] / 1000 [msg/tarfile] = 36 tarfiles
#            1 cpu rate ~30 tarfiles / hour (~30k msg/hour)

import os      as os
import tarfile as tarf

origin = '/data/daq.crayfis.io/raw'  # data source
export = './spiderjobs'  # destination folder
step   = 10   # data files per job

print '> data source: ' + origin
print '>              {} data files per job'.format(step)

tarfiles = []
for path, directories, files in os.walk( origin ):
    if '_old/' in path: continue

    for filename in files:
        if filename.endswith('.tar.gz'):
            tarfiles.append( os.path.join(path,filename) )
tarfiles = sorted( tarfiles, key=lambda k: k.lower(), reverse=True )

n_files = 0
for job_num, start in enumerate( xrange( 0, len(tarfiles), step ) ):
    with open( '{dest}/job_{job:0{digits}}.conf'.format( dest=export, job=job_num+1, digits=len(str(len(tarfiles)))-1 ), 'w' ) as job_file:
        for file in tarfiles[start : start + step]:
            job_file.write( file + '\n' )
    n_files += 1
    
print 'done, {} files created'.format(n_files)
