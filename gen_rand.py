# generates random strategies with population size of sys.argv[1]

import random
import sys

f = open(sys.argv[3], 'w')

def check_equal(strat, new_s):
    for i in range(len(strat)):
        if new_s == strat[i][:-1]:
            return i
    return -1

strat = []
for i in range(int(sys.argv[1])):
    new_strat = [round(random.uniform(0.0, 1.0), 2) for i in range(4)]
    ind = check_equal (strat, new_strat)
    if ind != -1:
        strat[ind][-1] += 1.
    else:
        strat.append(new_strat + [1.0])

f.write('0.00001\n')
f.write('3 ' + str(sys.argv[2]) + '\n')
for s in strat:
    w = ' '.join(map(str, s))
    f.write(w + '\n')
