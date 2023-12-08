from itertools import product

K_M = "6 767"
K,M = int(K_M.split()[0]), int(K_M.split()[1])

list_tcf = []
# for _ in range(K):
#     list_tcf.append([int(x) for x in input().split()])

data = """2 488512261 423332742
2 625040505 443232774
1 4553600
4 92134264 617699202 124100179 337650738
2 778493847 932097163
5 489894997 496724555 693361712 935903331 518538304"""
list_tcf2 = data.split('\n')


lists_tcf = []
for sublist in range(len(list_tcf2)):
    lists_tcf.append([int(l) for l in list_tcf2[sublist][1:].split()])
print(lists_tcf)


best_S = int()
combinations = list(product(*lists_tcf))
f = lambda x: x**2

for combination in combinations:
    S_t = sum([f(X) for X in combination])%M
    if S_t > best_S:
        best_S = S_t

print(best_S)

