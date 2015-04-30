import payoff_2pop as po
import random
import numpy as np
import matplotlib.pyplot as plt
from math import exp, isnan
import sys

# f_popn -> parameters for population n
f_pop1 = open('parameters.txt', 'r')
f_pop2 = open('parameters2.txt', 'r')
f_out = open(sys.argv[1], 'a')

eps1, b1, c1, strat1, total1 = po.read_parameters(f_pop1)
eps2, b2, c2, strat2, total2 = po.read_parameters(f_pop2)

# pop_ind is which population we're checking for: 0 for first, 1 for second
def check_extinct (ind, strat, pop_ind, payoff_mat, coop_mat):
    # not extinct
    if int(strat[ind][-1]) != 0:
        return (-1, -1, -1)
    # extinct -- take last strat, and replace extinct one
    # update strat
    strat[ind] = strat[-1]
    strat.pop()

    # update payoff_mat
    # if we have first population, we update the rows
    if pop_ind == 0:
        payoff_mat[ind] = payoff_mat[-1]
        coop_mat[0][ind] = coop_mat[0][-1]
        coop_mat[1][ind] = coop_mat[1][-1]
        payoff_mat.pop()
        coop_mat[0].pop()
        coop_mat[1].pop()

    # if we have the second population, we update the columns
    if pop_ind == 1:
        for i in range(len(payoff_mat)):
            payoff_mat[i][ind] = payoff_mat[i][-1]
            payoff_mat[i].pop()
            coop_mat[0][i][ind] = coop_mat[0][i][-1]
            coop_mat[1][i][ind] = coop_mat[1][i][-1]
            coop_mat[0][i].pop()
            coop_mat[1][i].pop()
    return (strat, payoff_mat, coop_mat)


# choose a strat randomly
def choose_strat (strat, pop_ind):
    if pop_ind == 0:
        c_ind = random.randint(1, int(total1))
    else:
        c_ind = random.randint(1, int(total2))
    partial = 0
    # find which strategy random int corresponds to
    for i in range(len(strat)):
        partial += strat[i][-1]
        if c_ind <= partial:
            return i
    return -1


# mutation event: a strat changes to random strat with prob mu
# strat_other is the other population's strategies - for calc payoffs
def mutation (strat_mut, strat_other, pop_ind, payoff_mat, coop_mat):
    new_strat = [round(random.uniform(0.0, 1.0), 2) for i in range(4)]
    L = len(strat_other)

    # calculate payoffs - add new_strat to end, pi_new append at end,
    # and vec of pi_new append at end
    new_payoffs = [0 for i in range(L)]
    new_coop = [[0 for i in range(L)] for j in range(2)]
    if pop_ind == 0:
        for i in range(L):
            pay1, pay2, coop1, coop2 = po.pairwise_payoff(new_strat, strat_other[i])
            new_payoffs[i] = (pay1, pay2)
            new_coop[0][i], new_coop[1][i] = coop1, coop2
        payoff_mat.append(new_payoffs)
        coop_mat[0].append(new_coop[0])
        coop_mat[1].append(new_coop[1])
    # second pop -- add a new column
    if pop_ind == 1:
        for i in range(L):
            pi_s, pi_new, coop1, coop2 = po.pairwise_payoff(strat_other[i], new_strat)
            payoff_mat[i].append((pi_s, pi_new))
            coop_mat[0][i].append(coop1)
            coop_mat[1][i].append(coop2)

    # add the strat
    strat_mut.append(new_strat + [1.0])

    # subtract one from the randomly selected strat
    ind = choose_strat(strat_mut, pop_ind)
    strat_mut[ind][-1] -= 1.

    # update payoff and strat order if extinct
    (s, pf, cm) = check_extinct(ind, strat_mut, pop_ind, payoff_mat, coop_mat)
    if (s, pf, cm) != (-1, -1, -1):
        strat_mut = s
        payoff_mat = pf
        coop_mat = cm
    return strat_mut, payoff_mat, coop_mat


# selection event with prob 1 - mu
def selection (s, strat, strat_other, pop_ind, payoff_mat, coop_mat):
    ind_l = choose_strat(strat, pop_ind)
    ind_r = choose_strat(strat, pop_ind)

    # if same strat chosen, no change
    if ind_l == ind_r:
        return strat, payoff_mat, coop_mat

    # calculate payoffs to calculate rho
    pi_l = po.total_payoff_strat(ind_l, pop_ind, strat_other, payoff_mat)
    pi_r = po.total_payoff_strat(ind_r, pop_ind, strat_other, payoff_mat)
    rho = 1./(1. + exp(-s*(pi_r - pi_l)))
    prob = random.uniform(0.0, 1.0)

    # if prob is < rho, then change one of strat_l to strat_r
    if prob < rho:
        strat[ind_l][-1] -= 1.
        strat[ind_r][-1] += 1.

    # update payoff matrix
    (s, pf, cm) = check_extinct(ind_l, strat, pop_ind, payoff_mat, coop_mat)
    if (s, pf, cm) != (-1, -1, -1):
        strat = s
        payoff_mat = pf
        coop_mat = cm
    return strat, payoff_mat, coop_mat

# s = strength of selection
# mu = prob of mutation, 1 - mu = prob of selection
# T = timesteps
# p = prob of event in pop 1, 1 - p = prob of event in pop 2
def evolve (s, mu, p, T, strat1, strat2):
    pmat, cmat = po.create_payoff_mat (strat1, strat2)
    coop1, coop2 = 0., 0.
    # number of evolutions
    for t in range(T):
        # mutation
        if random.uniform(0.0, 1.0) < mu:
            # whether in pop1 or pop2
            if random.uniform(0.0, 1.0) < p:
                strat1, pmat, cmat = mutation(strat1, strat2, 0, pmat, cmat)
            else:
                strat2, pmat, cmat = mutation(strat2, strat1, 1, pmat, cmat)
        # selection
        else:
            # whether in pop1 or pop2
            if random.uniform(0.0, 1.0) < p:
                strat1, pmat, cmat = selection(s, strat1, strat2, 0, pmat, cmat)
            else:
                strat2, pmat, cmat = selection(s, strat2, strat1, 1, pmat, cmat)
        coop1 += po.coop_avg_calc(strat1, cmat, 0)
        coop2 += po.coop_avg_calc(strat2, cmat, 1)
    return strat1, strat2, coop1/T, coop2/T

T = 10**7
s = 5
mu = 0.1
p = 0.5
strat1, strat2, coop1, coop2 = evolve (s, mu, p, T, strat1, strat2)

print c1
f_out.write(str(coop1) + ' ' + str(coop2) + '\n')
