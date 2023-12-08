#   Exercise 4.12: Fit Straight Line to Data
#    fit_straight_line.py
import numpy as np
import matplotlib.pyplot as plt
fig, ax1 = plt.subplots()

ts = np.linspace(0,10,101)

bs = [0.5,0.75,1.0,1.25,1.5]

def sinesum(t,b,n=1):
    S_N = 0
    for n in range(len(b)):
        S_N += b[n]*np.sin(n*t)
    return S_N

ys = []

plt.title(f"Final")
ax2 = ax1.twinx()
ax1.scatter(ts,sinesum(ts,bs), label="yi")

ax1.set_xlabel("x")
ax1.set_ylabel("y=f(x)")
ax1.legend()
plt.tight_layout()
plt.show()