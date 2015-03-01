import payoff
import random

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
    return i

def check_equal (strat, new_s):
    for i in range(len(strat)):
        if sorted(new_s) == sorted(strat[i][:-1]):
            return i
    return -1

def mutation (strat):
    new_strat = [round(random.uniform(0.0, 1.0), 2) for i in range(4)]

    # check if random new strat is same
    ind = check_equal (strat, new_strat)
    print ind
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

print mutation(strategies)

print payoff.total_payoff(strategies)

def selection (strat):
    ind_l = choose_strat(strat)
    ind_r = choose_strat(strat)
    payoffs = payoff.total_payoff(strat)


