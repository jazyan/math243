import payoff_2pop as po
import random
import numpy as np
import matplotlib.pyplot as plt
from math import exp, isnan

# f_popn -> parameters for population n
f_pop1 = open('parameters.txt', 'r')
f_pop2 = open('parameters2.txt', 'r')
f_out = open('avgpayoff.txt', 'a')

eps1, b1, c1, strat1, total1 = po.read_parameters(f_pop1)
eps2, b2, c2, strat2, total2 = po.read_parameters(f_pop2)

# pop_ind is which population we're checking for: 0 for first, 1 for second
def check_extinct (ind, strat, pop_ind, payoff_mat):
    # not extinct
    if int(strat[ind][-1]) != 0:
        return (-1, -1)
    # extinct -- take last strat, and replace extinct one
    # update strat
    strat[ind] = strat[-1]
    strat.pop()

    # update payoff_mat
    # if we have first population, we update the rows
    if pop_ind == 0:
        payoff_mat[ind] = payoff_mat[-1]
        payoff_mat.pop()

    # if we have the second population, we update the columns
    if pop_ind == 1:
        for row in payoff_mat:
            row[ind] = row[-1]
            row.pop()
    return (strat, payoff_mat)


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


# check if new_s is equal to already existing strat
def check_equal (strat, new_s):
    for i in range(len(strat)):
        if new_s == strat[i][:-1]:
            return i
    return -1


# mutation event: a strat changes to random strat with prob mu
# strat_other is the other population's strategies - for calc payoffs
def mutation (strat_mut, strat_other, pop_ind, payoff_mat):
    new_strat = [round(random.uniform(0.0, 1.0), 2) for i in range(4)]

    # check if random new strat is same
    ind = check_equal (strat_mut, new_strat)
    if ind != -1:
        strat[ind][-1] += 1.

    # if not the same, then add strat
    # calculate payoffs - add new_strat to end, pi_new append at end,
    # and vec of pi_new append at end
    else:
        # first pop -- add a new row
        if pop_ind == 0:
            new_payoffs = []
            for i in range(len(strat_other)):
                pi_new, pi_s = po.pairwise_payoff(new_strat, strat_other[i])
                new_payoffs.append((pi_new, pi_s))
            payoff_mat.append(new_payoffs)
        # second pop -- add a new column
        if pop_ind == 1:
            for i in range(len(strat_other)):
                pi_s, pi_new = po.pairwise_payoff(strat_other[i], new_strat)
                payoff_mat[i].append((pi_s, pi_new))

        # add the strat
        strat_mut.append(new_strat + [1.0])

    # subtract one from the randomly selected strat
    ind = choose_strat(strat_mut, pop_ind)
    strat_mut[ind][-1] -= 1.

    # update payoff and strat order if extinct
    (s, pf) = check_extinct(ind, strat_mut, pop_ind, payoff_mat)
    if (s, pf) != (-1, -1):
        strat_mut = s
        payoff_mat = pf
    return strat_mut, payoff_mat


# selection event with prob 1 - mu
def selection (s, strat, strat_other, pop_ind, payoff_mat):
    ind_l = choose_strat(strat, pop_ind)
    ind_r = choose_strat(strat, pop_ind)

    # if same strat chosen, no change
    if ind_l == ind_r:
        return strat, payoff_mat

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
    (s, pf) = check_extinct(ind_l, strat, pop_ind, payoff_mat)
    if (s, pf) != (-1, -1):
        strat = s
        payoff_mat = pf
    return strat, payoff_mat

# s = strength of selection
# mu = prob of mutation, 1 - mu = prob of selection
# T = timesteps
# p = prob of event in pop 1, 1 - p = prob of event in pop 2
def evolve (s, mu, p, T, strat1, strat2):
    mat = po.create_payoff_mat (strat1, strat2)

    # number of evolutions
    for t in range(T):
        print t
        # mutation
        if random.uniform(0.0, 1.0) < mu:
            # whether in pop1 or pop2
            if random.uniform(0.0, 1.0) < p:
                strat1, mat = mutation(strat1, strat2, 0, mat)
            else:
                strat2, mat = mutation(strat2, strat1, 1, mat)
        # selection
        else:
            # whether in pop1 or pop2
            if random.uniform(0.0, 1.0) < p:
                strat1, mat = selection(s, strat1, strat2, 0, mat)
            else:
                strat2, mat = selection(s, strat2, strat1, 1, mat)
        '''
        # store every 100th avg payoff for payoff graph
        if t % 100 == 0:
            pay1, pay2 = po.total_payoff(strat1, strat2, mat)
            avg = sum([strat[i][-1]*payoffs[i] for i in range(len(strat))])
            avg_payoff.append(float(avg)/float(total))
        '''
    return strat1, strat2

# calc avg p_cc, p_cd, p_dc, p_dd
def avg_payoff(strat):
    avg = np.array([0. for i in range(4)])
    for s in strat:
        avg += np.array([s[i]*s[-1] for i in range(4)])
    return [round(t/float(total), 4) for t in avg]

T = 10**7
s = 100
mu = 0.001
p = 0.5
strat1, strat2 = evolve (s, mu, p, T, strat1, strat2)
print "STRAT1", strat1
print "STRAT2", strat2
#avg = avg_payoff(strat)

'''
# graph the average payoff
y = np.array(y)
x = np.arange(1, T/100 + 1)
plt.xlim((0, T/100+1))
plt.ylim((min(y) - 10, max(y) + 10))
plt.scatter(x, y)
plt.show()

# write the final average payoff
f_out.write(str(total) + ' ' + str(y[-1]) + ' ' + ' '.join(map(str, avg)) + '\n')
'''
