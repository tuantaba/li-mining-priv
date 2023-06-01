#!/bin/bash

input_IP_file="input.lst"
outputtxt="output.txt"
# service="controller-to-other-service"
protocol="PING"
location="WAN-HCM"
outputjson="output.json"

#remove duplicated IP with check_tcp.txt file


json_template='  {
    "targets": [
      "%s"
    ],
    "labels": {
      "service": "%s",
      "protocol": "%s",
      "location": "%s"
    }
  }'
# echo $json_template

i=0
j=0

echo -e  "[ \n"  >  $outputjson

for l in `seq 1 $(cat $input_IP_file |wc -l)`
do
  j=$((j+1))
done

echo "Generate alert number: $j"
for l in `seq 1 $(cat $input_IP_file |wc -l)`
do
    i=$((i+1))
    line=$(awk "NR==$i" $input_IP_file)
    _IP=$(echo $line|awk '{print $1}')
    _SERVICE=$(echo $line|awk '{print $2}')
    printf "$json_template" "$_IP" "$_SERVICE" "$protocol" "$location"   >> $outputjson
    # echo $i 
    if [ $i -lt $j ]
    then
        echo -e ", \n" >> $outputjson
    else
      echo -e "\n" >> $outputjson
    fi

done
echo "]"  >>   $outputjson

echo "path json is exported to $outputjson"