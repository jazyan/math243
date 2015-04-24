#!/bin/bash

echo "Script is starting"

cp empty.txt avgpayoff1.txt

for i in `seq 1 5`;
do
    python gen_rand.py 100 parameters.txt
    python gen_rand.py 100 parameters2.txt
    time python evolution_2pop.py 0.1 avgpayoff1.txt
done

echo "Done"
exit 0
