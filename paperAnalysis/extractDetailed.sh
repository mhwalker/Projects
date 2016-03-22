#!/bin/bash

tmpfile=html.list

ls -l *.html | awk '{print $9}' > $tmpfile

#cat $tmpfile
while read line
do
    outfilename=`echo $line | sed "s/html/record/"`
    echo $outfilename
    grep "Detailed record" $line | awk '{split($4,array,"\""); print array[2];}' > $outfilename
done < $tmpfile
rm $tmpfile
