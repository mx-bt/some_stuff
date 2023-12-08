# calculate definite integrals using monte carlo method

import numpy as np

# set seed
np.random.seed(8272)

def f(x):
    return np.log(x) * np.sin(10*x) + 1.0

# integration from ... to ...
xmin = 1.0
xmax = 2.0

# y range
ymin = 0.0
ymax = 2.0

# number of points
n = 10000000

# n random x,y values and corresponding f(x)
x  = np.random.uniform(1.0, 2.0, n)
y  = np.random.uniform(0.0, 2.0, n)
fx = f(x)

count = 0
for i in range(n):
    if y[i] <= fx[i]:
        count += 1

print("approximate value =", count/n * (xmax-xmin)*(ymax-ymin))

