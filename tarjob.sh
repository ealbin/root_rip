#!/bin/bash

# bundles tar.gz data files specified in spiderjobs as a tar.gz
# transmitts back to gpatlas

echo '   [craydata]: preparing files for transfer...'

if [ $# -eq 0 ]; then
    echo 'sausage: bash tarjob.sh [job_####.conf]'
    exit
fi

if [ -e /home/ealbin/root_rip/donejobs/${1/%.conf} ]; then
    rm -rf /home/ealbin/root_rip/donejobs/${1/%.conf} ]
fi
mkdir -p /home/ealbin/root_rip/donejobs/${1/%.conf}

home=/home/ealbin/root_rip/spiderjobs
out=${1/%conf}tar.gz  # e.g. job_0123.conf -> job_0123.tar.gz
cd /home/ealbin/root_rip/donejobs/${1/%.conf}
tar -czvPf $home/$out -T $home/$1
echo '   [craydata]: transfering...'
scp $home/$out ealbin@gpatlas1.ps.uci.edu:$home
rm $home/$out
