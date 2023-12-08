#   Exercise 4.12: Fit Straight Line to Data
#    fit_straight_line.py
import numpy as np
import matplotlib.pyplot as plt
fig, ax1 = plt.subplots()

yis = [0.5,
       2.0,
       1.0,
       1.5,
       7.5
      ]
xis = np.linspace(0,4,len(yis))

a = 5#int(input("Input initial value for a(int): "))
b = -10#int(input("Input initial value for b(int): "))
search_step = 0.02#float(input("Input the size of each linear search step: "))
epsilon = 0.0000001 #float(input("Desired precision(float): "))

def line(x,a,b):
    return(a*x+b)
def e(yis,xis,a,b):
    if len(yis) != len(xis):
        print("Yi and Xi arrays aren't equal")
        pass
    sum_e = 0
    for i in range(len(yis)):
        sum_e += (line(xis[i],a,b) - yis[i])**2
    return sum_e

errors = [e(yis,xis,a,b)]
print("Initial rror: ",errors)
cnt = 0
delta = np.inf
while (delta > epsilon) and cnt <= 1000:
    cnt += 1
    a_try1 = a+search_step
    a_try2 = a-search_step
    if e(yis,xis,a_try2,b) < e(yis,xis,a_try1,b):
        candidate = a_try2
    else:
        candidate = a_try1
    if e(yis,xis,candidate,b) < errors[cnt-1]:
        a = candidate
    else:
        pass

    b_try1 = b+search_step
    b_try2 = b-search_step
    if e(yis,xis,a,b_try2) < e(yis,xis,a,b_try1):
        candidate = b_try2
    else:
        candidate = b_try1
    if e(yis,xis,a,candidate) < errors[cnt-1]:
        b = candidate
    else:
        pass
    errors.append(e(yis,xis,a,b))
    print("Error: ",errors[cnt])
    delta = np.abs(errors[cnt-1]-errors[cnt])

    if cnt == 1000:
        print("No convergence after 1000 iterations")
        print(f"The best parameters are: a={a}, b={b}")
        print(f"Initial error= {errors[1]}")
        print(f"Lowest error= {errors[cnt]}")
    else:
        ("Fail pass")
        pass

if delta < epsilon:
    print(f"Convergence after {cnt} iterations")
    print(f"The best parameters are: a={a}, b={b}")
    print(f"Initial error= {errors[1]}")
    print(f"Lowest error= {errors[cnt]}")

line_plot = []
for i in range(len(xis)):
    line_plot.append(line(xis[i],a,b))
ax1.plot(xis,line_plot,label="predictions")


plt.title(f"Final error={e(yis,xis,a,b)} after {cnt} iterations")
ax2 = ax1.twinx()
ax1.scatter(xis,yis, label="yi")
ax1.set_xlabel("x")
ax1.set_ylabel("y=f(x)")
ax1.legend()
plt.tight_layout()
plt.show()