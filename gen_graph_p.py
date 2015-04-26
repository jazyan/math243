import matplotlib.pyplot as plt
import numpy as np

f = open('avgcoop_p.txt', 'r')

x = [0.1, 0.3, 0.5, 0.7, 0.9]
T1, T2 = 0., 0.
avg_val1 = [0 for i in range(5)]
avg_val2 = [0 for i in range(5)]

for i in range(len(x)*5):
    val1, val2 = map(float, f.readline().split())
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
plt.plot(x, avg_val1, '*-', label='pop 1')
plt.plot(x, avg_val2, '*-', label='pop 2')
plt.legend()
plt.show()
