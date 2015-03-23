import payoff_mat as payoff
import random
import numpy as np
import matplotlib.pyplot as plt
from math import exp, isnan

f_in = open('parameters2.txt', 'r')
f_out = open('avgpayoff.txt', 'a')

eps, b, c, strategies, total = payoff.read_parameters(f_in)

def check_extinct (ind, strat, payoff_mat):
    # not extinct
    if int(strat[ind][-1]) != 0:
        return (-1, -1)
    # extinct -- take last strat, and replace extinct one
    # update strat
    strat[ind] = strat[-1]
    strat.pop()

    # update payoff_mat: move last row to ind, remove last row
    payoff_mat[ind] = payoff_mat[-1]
    payoff_mat.pop()

    # for each row, replace ind item with last one
    for pf in payoff_mat:
        pf[ind] = pf[-1]
        pf.pop()
    return (strat, payoff_mat)


# choose a strat randomly
def choose_strat (strat):
    c_ind = random.randint(1, int(total))
    partial = 0
    # find which strategy random int corresponds to
    for i in range(len(strat)):
        partial += strat[i][-1]
        if c_ind <= partial:
            return i
    return -1


# check if new_s is equal to already existing strat
def check_equal (strat, new_s):
    for i in range(len(strat)):
        if new_s == strat[i][:-1]:
            return i
    return -1


# mutation event: a strat changes to random strat with prob mu
def mutation (strat, payoff_mat):
    new_strat = [round(random.uniform(0.0, 1.0), 2) for i in range(4)]

    # check if random new strat is same
    ind = check_equal (strat, new_strat)
    if ind != -1:
        strat[ind][-1] += 1.

    # if not the same, then add strat
    # calculate payoffs - add new_strat to end, pi_new append at end,
    # and vec of pi_new append at end
    else:
        new_payoffs = []
        for i in range(len(strat)):
            pi_new, pi_s = payoff.pairwise_payoff(new_strat, strat[i])
            payoff_mat[i].append(pi_s)
            new_payoffs.append(pi_new)
        # calc its payoff with itself
        pi_s1, pi_s2 = payoff.pairwise_payoff(new_strat, new_strat)
        new_payoffs.append(pi_s1)
        payoff_mat.append(new_payoffs)
        # add the strat
        strat.append(new_strat + [1.0])

    # subtract one from the randomly selected strat
    ind = choose_strat(strat)
    strat[ind][-1] -= 1.

    # update payoff and strat order if extinct
    (s, pf) = check_extinct(ind, strat, payoff_mat)
    if (s, pf) != (-1, -1):
        strat = s
        payoff_mat = pf
    return strat, payoff_mat


# selection event with prob 1 - mu
def selection (s, strat, payoff_mat):
    ind_l = choose_strat(strat)
    ind_r = choose_strat(strat)

    # if same strat chosen, no change
    if ind_l == ind_r:
        return strat, payoff_mat

    # calculate payoffs to calculate rho
    payoffs = payoff.total_payoff(strat, payoff_mat)
    pi_l, pi_r = payoffs[ind_l], payoffs[ind_r]
    rho = 1./(1. + exp(-s*(pi_r - pi_l)))
    prob = random.uniform(0.0, 1.0)

    # if prob is < rho, then change one of strat_l to strat_r
    if prob < rho:
        strat[ind_l][-1] -= 1.
        strat[ind_r][-1] += 1.

    # update payoff matrix
    (s, pf) = check_extinct(ind_l, strat, payoff_mat)
    if (s, pf) != (-1, -1):
        strat = s
        payoff_mat = pf
    return strat, payoff_mat

# s = strength of selection
# mu = prob of mutation, 1 - mu = prob of selection
# T = timesteps

def evolve (s, mu, T, strat):
    payoff_mat = payoff.create_payoff_mat (strat)
    avg_payoff = []

    # number of evolutions
    for t in range(T):
        if random.uniform(0.0, 1.0) < mu:
            strat, payoff_mat = mutation(strat, payoff_mat)
        else:
            strat, payoff_mat = selection(s, strat, payoff_mat)
        # store every 100th avg payoff for payoff graph
        if t % 100 == 0:
            payoffs = payoff.total_payoff(strat, payoff_mat)
            avg = sum([strat[i][-1]*payoffs[i] for i in range(len(strat))])
            avg_payoff.append(float(avg)/float(total))
    return strat, avg_payoff

# calc avg p_cc, p_cd, p_dc, p_dd
def avg_payoff(strat):
    avg = np.array([0. for i in range(4)])
    for s in strat:
        avg += np.array([s[i]*s[-1] for i in range(4)])
    return [round(t/float(total), 4) for t in avg]

T = 10**7
s = 100
mu = 0.01
strat, y = evolve(s, mu, T, strategies)
#print "STRAT", strat
avg = avg_payoff(strat)

'''
# graph the average payoff
y = np.array(y)
x = np.arange(1, T/100 + 1)
plt.xlim((0, T/100+1))
plt.ylim((min(y) - 10, max(y) + 10))
plt.scatter(x, y)
plt.show()
'''

# write the final average payoff
f_out.write(str(total) + ' ' + str(y[-1]) + ' ' + ' '.join(map(str, avg)) + '\n')
