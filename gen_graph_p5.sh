#!/bin/bash

echo "Script is starting"

cp empty.txt avgpayoff5.txt

for i in `seq 1 10`;
do
    python gen_rand.py 100 2 parameters.txt
    python gen_rand.py 100 1 parameters2.txt
    time python evolution_2pop.py avgpayoff5.txt
done

echo "Done"
exit 0
