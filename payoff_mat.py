import numpy as np
import math

# input file has:
# eps
# b c
# strat: q_cc q_cd q_dc q_dd num
f_in = open('parameters2.txt', 'r')

# output file has expected payoffs
f_out = open('avgpayoff_2.txt', 'w')

# returns info read from file
def read_parameters (f):
    eps = float(f.readline())
    b, c = map(float, f.readline().split())
    strategies = []
    total = 0
    for line in f:
        new_strat = map(float, line.split())
        total += new_strat[-1]
        strategies.append(new_strat)
    total = float(total)
    return eps, b, c, strategies, total

eps, b, c, strategies, total = read_parameters(f_in)

# to ensure the matrix is ergodic
def error (strat):
    error = [(1.-eps)*strat[i] + eps*(1-strat[i]) for i in range(4)]
    error.append(strat[-1])
    return error

# calculates the payoff b/w strat1 and strat2
def pairwise_payoff (strat1, strat2):
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
    #I = np.identity(4)
    #M = transition - I
    #'''
    eig_val, eig_vec = np.linalg.eig(transition)
    eig_vec = np.around(eig_vec, decimals=2)

    # find index of vector with eig val = 1
    eig_val = [round(i, 5) for i in eig_val]
    ind = list(eig_val).index(1.)

    # might be scalar multiple, need to normalize so sum to 1
    eig_vec = [elt/sum(list(eig_vec[:,ind])) for elt in eig_vec[:,ind]]
    '''
    zero = np.array([0, 0, 0, 0])
    ans = np.linalg.lstsq(M, zero)
    print ans
    print
    '''
    # expected payoffs
    pay_1 = eig_vec[0]*(b-c) + eig_vec[1]*(-c) + eig_vec[2]*b
    pay_2 = eig_vec[0]*(b-c) + eig_vec[1]*(b) + eig_vec[2]*(-c)

    return pay_1, pay_2

# weight the payoffs based on how many have the strategy
def weight_payoff (N1, N2, pay_1, pay_2, self):
    if self:
        return pay_1*(N2 - 1)/(total - 1)
    return (pay_1*N2/(total - 1), pay_2*N1/(total - 1))


# row i has strat i's payoffs against the rest of the strats
def create_payoff_mat (strat):
    mat = [[0 for i in range(len(strat))] for j in range(len(strat))]
    for i in range(len(strat)):
        pay_ii, pay_ii = pairwise_payoff(strat[i], strat[i])
        mat[i][i] = pay_ii
        for j in range(i+1, len(strat)):
            pay_ij, pay_ji = pairwise_payoff(strat[i], strat[j])
            mat[i][j] = pay_ij
            mat[j][i] = pay_ji
    return mat

# calculates total payoff
def total_payoff(strat, payoff_mat):
    totals = [0 for i in range(len(strat))]
    for i in range(len(strat)):
        # if strat[i][-1] = 1, then no weighted payoff against self
        if strat[i][-1] != 1:
            pay_1 = payoff_mat[i][i]
            pi_ii = weight_payoff(strat[i][-1], strat[i][-1], pay_1, pay_1, 1)
            totals[i] += pi_ii

        # add weighted payoffs against rest of players
        for j in range(i+1, len(strat)):
            pay_1 = payoff_mat[i][j]
            pay_2 = payoff_mat[j][i]
            pi_ij, pi_ji = weight_payoff(strat[i][-1], strat[j][-1], pay_1, pay_2, 0)
            totals[i] += pi_ij
            totals[j] += pi_ji
    return map(float, totals)

if __name__ == '__main__':
    payoff_mat = create_payoff_mat (strategies)
    for t in total_payoff(strategies, payoff_mat):
        f_out.write(str(t) + "\n")
