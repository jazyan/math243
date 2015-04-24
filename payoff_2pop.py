import numpy as np
import math

# input file has:
# eps
# b c
# strat: q_cc q_cd q_dc q_dd num
# f_pop1 has strategies for pop1
f_pop1 = open('parameters.txt', 'r')
f_pop2 = open('parameters2.txt', 'r')

# output file has expected payoffs
f_out = open('avgpayoff_3.txt', 'w')

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

eps, b1, c1, strat1, total1 = read_parameters(f_pop1)
eps, b2, c2, strat2, total2 = read_parameters(f_pop2)


# to ensure the matrix is ergodic
def error (strat):
    error = [(1.-eps)*strat[i] + eps*(1-strat[i]) for i in range(4)]
    error.append(strat[-1])
    return error


def null(A, eps = 1e-15):
    u, s, vh = np.linalg.svd(A)
    null_mask = (s <= eps)
    null_space = np.compress(null_mask, vh, axis=0)
    S = sum(list(null_space[0]))
    return [round(n, 2)/S for n in null_space[0]]


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
    I = np.identity(4)
    M = transition - I

    eig_vec = null(M)

    # expected payoffs
    pay_1 = eig_vec[0]*(b1-c1) + eig_vec[1]*(-c1) + eig_vec[2]*b1
    pay_2 = eig_vec[0]*(b2-c2) + eig_vec[1]*(b2) + eig_vec[2]*(-c2)
    # average coop
    avg_coop = eig_vec[0] + 0.5*(eig_vec[1] + eig_vec[2])
    return pay_1, pay_2, avg_coop


# create payoff matrices with pop_1 as rows, and pop_2 as cols
# each entry is (pay_1_ij, pay_2_ij)
def create_payoff_mat (strat_1, strat_2):
    L1 = len(strat_1)
    L2 = len(strat_2)

    pay_mat = [[0 for i in range(L2)] for j in range(L1)]
    coop_mat = [[0 for i in range(L2)] for j in range(L1)]

    for i in range(L1):
        for j in range(L2):
            pay_1, pay_2, avg_coop = pairwise_payoff(strat_1[i], strat_2[j])
            pay_mat[i][j] = (pay_1, pay_2)
            coop_mat[i][j] = avg_coop
    return pay_mat, coop_mat


# calculates payoff for single strat S at index i
# other_pop is the popluation that S is NOT in, mat is the payoff matrix
# ind = 0 means first pop, ind = 1 means second pop
def total_payoff_strat (i, ind, other_pop, mat):
    total_num = 0
    total_payoff = 0
    L = len(other_pop)
    # if we're in the first pop, then read across rows, first entry
    if ind == 0:
        for l in range(L):
            n = other_pop[l][-1]
            total_payoff += n*mat[i][l][0]
            total_num += n
    else:
        for l in range(L):
            n = other_pop[l][-1]
            total_payoff += n*mat[l][i][1]
            total_num += n
    return total_payoff/total_num


# calculates total payoffs for both populations
def total_payoff(strat_1, strat_2, mat):
    L1 = len(strat_1)
    L2 = len(strat_2)

    totals_1 = [total_payoff_strat(i, 0, strat_2, mat) for i in range(L1)]
    totals_2 = [total_payoff_strat(i, 1, strat_1, mat) for i in range(L2)]
    return totals_1, totals_2

def coop_avg_calc (strat_1, mat):
    total = [s[-1] for s in strat_1]
    S = sum(total)
    totals = np.array(total)/S
    dot_prod = np.dot(totals, np.array(mat))
    return np.sum(dot_prod)/len(mat[0])

if __name__ == '__main__':
    payoff_mat, coop_mat = create_payoff_mat (strat1, strat2)
    t1, t2 = total_payoff(strat1, strat2, payoff_mat)
    avg_coop = coop_avg_calc(strat1, coop_mat)
    f_out.write("Pop 1 payoffs\n")
    for t in t1:
        f_out.write(str(t) + "\n")
    f_out.write("Pop 2 payoffs\n")
    for t in t2:
        f_out.write(str(t) + "\n")
    f_out.write("Avg cooperation: " + str(avg_coop) + '\n')
