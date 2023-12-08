N = int(input("Enter positive integer: "))
import random as rd
nmbrs = []
M = 0
for i in range(N):
    nmbr = rd.randint(1,6)
    nmbrs.append(nmbr)
    if nmbr == 6:
        M += 1
print(nmbrs)
print(M)
print("Ratio of 6's: ",round(M/N,3),"%")


