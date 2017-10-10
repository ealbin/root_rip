#!/bin/bash

if [ -e compared ]; then
    rm -f compared
fi
ls devices  -s  > _A
ls data     -s  > _B
ls devices  -sh > _Ah
ls data     -sh > _Bh

D=(`ls data | sed 's/.root//'`)

for d in ${D[@]}; do
    a=$(egrep $d _A | awk '{print $1}')
    b=$(egrep $d _B | awk '{print $1}')
    c=$(echo "($b - $a)/$a * 100" | bc -l | xargs printf "%0.0f")

    ah=$(egrep $d _Ah | awk '{print $1}')
    bh=$(egrep $d _Bh | awk '{print $1}')

    echo -e "$d:    \t ${ah}    \t->\t${bh}      \t => \t $c %" >> compared
done

sort -nk6 compared > _tmp && mv _tmp compared
rm -f _A _B _Ah _Bh

head compared
echo "..."
tail compared
echo "(full listing: ./compared)"
