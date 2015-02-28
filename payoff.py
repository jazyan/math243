import numpy as np
import math

# input file has:
# b c
# strat: q_cc q_cd q_dc q_dd num
f_in = open('parameters.txt', 'r')

# output file has expected payoffs
f_out = open('avgpayoff.txt', 'w')

eps = 0.00000001

b, c = map(float, f_in.readline().split())
strategies = []
total = 0
for line in f_in:
    new_strat = map(float, line.split())
    total += new_strat[-1]
    strategies.append(new_strat)
total = float(total)

def error (strat):
    error = [(1.-eps)*strat[i] + eps*(1-strat[i]) for i in range(4)]
    error.append(strat[-1])
    return error

def pairwise_payoff (strat1, strat2, self):
    # add error to strategies
    p_c = error(strat1)
    q_c = error(strat2)

    # make sure in perspective of p_c
    new_q_c = q_c[:]
    new_q_c[1] = q_c[2]
    new_q_c[2] = q_c[1]

    # matrix of prob: CC, CD, DC, DD
    transition = np.array([[p_c[i]*new_q_c[i] for i in range(4)],
        [p_c[i]*(1 - new_q_c[i]) for i in range(4)],
        [(1 - p_c[i])*new_q_c[i] for i in range(4)],
        [(1 - p_c[i])*(1 - new_q_c[i]) for i in range(4)]])
    eig_val, eig_vec = np.linalg.eig(transition)
    eig_vec = np.around(eig_vec, decimals=2)

    # find index of vector with eig val = 1
    ind = list(map(round, eig_val)).index(1.)

    # might be scalar multiple, need to normalize so sum to 1
    eig_vec = [elt/sum(list(eig_vec[:,ind])) for elt in eig_vec[:,ind]]

    # expected payoffs
    pay_1 = eig_vec[0]*(b-c) + eig_vec[1]*(-c) + eig_vec[2]*b
    pay_2 = eig_vec[0]*(b-c) + eig_vec[1]*(b) + eig_vec[2]*(-c)
    if self:
        weight_1 = (q_c[-1] - 1)/(total - 1)
        weight_2 = (p_c[-1] - 1)/(total - 1)
    else:
        weight_1 = q_c[-1]/(total - 1)
        weight_2 = p_c[-1]/(total - 1)
    return (weight_1*pay_1, weight_2*pay_2)


def total_payoff(strat):
    totals = [0 for i in range(len(strat))]
    for i in range(len(strat)):
        if strat[i][-1] != 1:
            pi_ii, pi_ii = pairwise_payoff(strat[i], strat[i], 1)
            totals[i] += pi_ii
        for j in range(i+1, len(strat)):
            pi_ij, pi_ji = pairwise_payoff(strat[i], strat[j], 0)
            totals[i] += pi_ij
            totals[j] += pi_ji
    return totals

if __name__ == '__main__':
    for t in total_payoff(strategies):
        f_out.write(str(t) + "\n")
