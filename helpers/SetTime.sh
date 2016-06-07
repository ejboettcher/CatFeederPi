#!/bin/bash
# Read in the time from the android phone and reset the android clock.g
s=$(head -n 1 ~/script/PhoneTime/phonetime.txt)
IN=$s

OIFS=$IFS
IFS="_"
arr=$IN
ii=0
for i in ${arr[@]}; do
  if [ $ii -eq "0" ]; then
    phonedate=$i
  fi
  if [ $ii -eq "1" ]; then
    phonetime=$i
  fi

  let "ii += 1"
  
done

IFS=$OIFS

#sudo date +%Y%m%d %H:%M:%S -s $phonedate $phonetime
#sudo date --set=$phonetime
sudo date --set="$phonedate $phonetime"