#!/bin/bash

echo "Script is starting"

let "outer = 1"
for j in 0.1 0.3 0.5 0.7 0.9
do
    let "inner = 1"
    for i in 1 2 3 4 5;
    do
        echo $i $j
        python gen_rand.py 100 parameters.txt
        python gen_rand.py 100 parameters2.txt
        time python evolution_2pop.py $j
    done
    let "outer+=1"
    echo
done

echo "Done"
exit 0
