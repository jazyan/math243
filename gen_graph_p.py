import matplotlib.pyplot as plt
import numpy as np

f = open('avgcoop_p.txt', 'r')

x = [0.1, 0.3, 0.5, 0.7, 0.9]
val_plot = [x for i in range(5)]
val_plot = sorted([j for i in val_plot for j in i])
T1, T2 = 0., 0.
pop1_val = []
pop2_val = []
avg_val1 = [0 for i in range(5)]
avg_val2 = [0 for i in range(5)]

for i in range(len(x)*5):
    val1, val2 = map(float, f.readline().split())
    pop1_val.append(val1)
    pop2_val.append(val2)
    if i % 5 == 4:
        T1 += val1
        T2 += val2
        avg_val1[i/5] = T1/5.
        avg_val2[i/5] = T2/5.
        T1, T2 = 0., 0.
    else:
        T1 += val1
        T2 += val2

plt.title('Relative speed of evolution')
plt.xlim((0.1, 0.9))
plt.xlabel('% evolution iterations in pop 1')
plt.ylabel('Avg Cooperation')
print np.array(avg_val1) - np.array(avg_val2)
#plt.plot(x, avg_val1, '*-', label='pop 1')
#plt.plot(val_plot, pop1_val, 'g^')
plt.plot(x, avg_val2, '*-', label='pop 2')
plt.plot(val_plot, pop2_val, 'r^')
plt.legend()
plt.show()
