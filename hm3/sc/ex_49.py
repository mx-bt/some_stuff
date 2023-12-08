#   Exercise 4.9: Find Crossing Points of Two Graphs
#   crossing_2_graphs.py

"""
g = lambda x: x**2
# ...which is equivalent to:
def g(x):
    return x**2
"""
import numpy as np

f = lambda x: x
g = lambda x: x**2

interval = [-4,4]

epsilon = float(input("Input desired precision: "))
N = int(input("Enter desired maximum of iterations: "))
x_range = np.linspace(interval[0],interval[1],N)
intersections = []
for x in x_range:
	if abs(f(x)-g(x)) < epsilon:
		intersections.append(x)
	else:
		pass

print(intersections)

"""
Output
Input desired precision: 0.01
Enter desired maximum of iterations: 400
[0.010025062656641381, 0.9924812030075181]

This means, for x1=0.01 and x2=0.992 the difference between f(x) and g(x)
is smaller than 0.01
The greater the value for epsilon, the more solutions
The greater the value for N, the more precise the best solution gets
"""