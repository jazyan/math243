#!/bin/bash

echo "Script is starting"

cp empty.txt avgpayoff4.txt

for i in `seq 1 5`;
do
    python gen_rand.py 100 3.75 parameters.txt
    python gen_rand.py 100 3 parameters2.txt
    time python evolution_2pop.py avgpayoff4.txt
done

echo "Done"
exit 0
