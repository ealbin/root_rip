#!/bin/bash

# bundles tar.gz data files specified in spiderjobs as a tar.gz
# transmitts back to gpatlas

echo '[craydata]: preparing files'
echo '----------------------------'

if [ $# -eq 0 ]; then
    echo 'sausage: bash tarjob.sh [job_####.conf]'
    exit
fi

home=/home/ealbin/root_rip/spiderjobs
out=${1/%conf}tar.gz

tar -cvzPf $home/$out -T $home/$1
scp $home/$out ealbin@gpatlas1.ps.uci.edu:$home
rm $home/$out

echo '[craydata]: done!'
