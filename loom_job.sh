#!/bin/bash

if [ -z $1 ]; then
	echo 'sausage: bash loom_job.sh TARFILE'
	exit
fi

# random delay 1 to d sec
#sleep $[ ( $RANDOM % (60*5) ) + 1 ]s

echo
name="${1/%\.tar\.gz}"
wd=/home/ealbin/scratch/${name}
mkdir -v /home/ealbin/scratch
if [ -e $wd ]; then
    rm -frv $wd
fi
mkdir -v $wd

# gpatlas home
cd /home/ealbin/root_rip

echo -e "\n"'[fun_job.sh]: working on' $1
echo '---------------------------------------------'

if [ -e /home/ealbin/root_rip/out/${name}.root ]; then
    echo '[fun_job.sh]: found completed job, skipping...'
    exit
fi

echo -e "\n"'[fun_job.sh]: fetching from craydata'
echo '---------------------------------------------'
cp -v /home/ealbin/root_rip/devices/$1 $wd

echo -e "\n"'[fun_job.sh]: extracting data'
echo '---------------------------------------------'
cd $wd
tar -xvzf $1 -C $wd
if [ $? -ne 0 ]; then echo 'ERROR - extraction issue'; exit; fi
rm -v $1
if [ $? -ne 0 ]; then echo 'ERROR - deletion issue'; exit; fi
echo '[fun_job.sh]: done'

echo -e "\n"'[fun_job.sh]: running loom'
echo '---------------------------------------------'
python /home/ealbin/root_rip/loom.py $wd $wd
if [ $? -ne 0 ]; then echo 'ERROR - loom issue'; exit; fi
echo '[fun_job.sh]: done'

echo -e "\n"'[fun_job.sh]: exporting to craydata'
echo '---------------------------------------------'
mv -v $wd/${name}.root /home/ealbin/root_rip/out/
echo '[fun_job.sh]: done'

echo -e "\n"'[fun_job.sh]: removing files'
echo '---------------------------------------------'
rm -rfv $wd
echo '[fun_job.sh]: done done, exiting'
echo
