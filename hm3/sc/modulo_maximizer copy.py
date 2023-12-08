# Enter your code here. Read input from STDIN. Print output to STDOUT
from itertools import product

K_M = input()#"3 1000"
K,M = int(K_M.split()[0]), int(K_M.split()[1])

lists_tcf = [] # -s !!
for _ in range(K):
    lists_tcf.append([int(x) for x in input().split()])

best_S = int()
combinations = list(product(*lists_tcf))
f = lambda x: x**2

for combination in combinations:
    S_t = sum([f(X) for X in combination])%M
    if S_t > best_S:
        best_S = S_t
        
print(best_S)