import payoff
import random
import numpy as np
import matplotlib.pyplot as plt
from math import exp, isnan

f_in = open('parameters.txt', 'r')
f_out = open('avgpayoff.txt', 'w')

eps, b, c, strategies, total = payoff.read_parameters(f_in)

def check_extinct (strat):
    return [s for s in strat if int(s[-1]) != 0]

def choose_strat (strat):
    c_ind = random.randint(1, int(total))
    partial = 0
    for i in range(len(strat)):
        partial += strat[i][-1]
        if c_ind <= partial:
            return i
    return -1

def check_equal (strat, new_s):
    for i in range(len(strat)):
        if sorted(new_s) == sorted(strat[i][:-1]):
            return i
    return -1

def mutation (strat):
    new_strat = [round(random.uniform(0.0, 1.0), 2) for i in range(4)]

    # check if random new strat is same
    ind = check_equal (strat, new_strat)
    if ind != -1:
        strat[ind][-1] += 1.
    # if not the same, then add strat
    else:
        strat.append(new_strat + [1.0])

    # subtract one from the randomly selected strat
    ind = choose_strat(strat)
    strat[ind][-1] -= 1.
    strat = check_extinct(strat)
    return strat

def selection (s, strat):
    ind_l = choose_strat(strat)
    ind_r = choose_strat(strat)
    payoffs = payoff.total_payoff(strat)
    pi_l, pi_r = payoffs[ind_l], payoffs[ind_r]
    rho = 1./(1. + exp(-s*(float(pi_r) - float(pi_l))))
    prob = random.uniform(0.0, 1.0)

    # if prob is < rho, then change one of strat_l to strat_r
    if prob < rho:
        strat[ind_l][-1] -= 1.
        strat[ind_r][-1] += 1.
    return check_extinct(strat)

# s = strength of selection
# mu = prob of mutation, 1 - mu = prob of selection
# T = timesteps

def evolve (s, mu, T, strat):
    avg_payoff = []
    for t in range(T):
        if random.uniform(0.0, 0.1) < mu:
            strat = mutation(strat)
        else:
            strat = selection(s, strat)
        payoffs = payoff.total_payoff(strat)
        avg = sum([strat[i][-1]*payoffs[i] for i in range(len(strat))])
        avg_payoff.append(float(avg))
    return strat, avg_payoff

T = 1000
strat, y = evolve(100, 0.1, T, strategies)
print "STRAT", strat
y = np.array(y)
x = np.arange(1, T+1)
plt.xlim((0, T+5))
plt.ylim((min(y) - 10, max(y) + 10))
plt.scatter(x, y)
plt.show()

