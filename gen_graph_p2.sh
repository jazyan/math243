#!/bin/bash

echo "Script is starting"

cp empty.txt avgpayoff2.txt

for i in `seq 1 5`;
do
    python gen_rand.py 20 1 parameters.txt
    python gen_rand.py 100 1 parameters2.txt
    time python evolution_2pop.py avgpayoff2.txt
done

echo "Done"
exit 0
