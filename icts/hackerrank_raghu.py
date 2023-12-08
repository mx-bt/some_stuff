from collections import Counter as C

# Inputs
X = int(input("X: "))

shoes = input("Shoes: ") # shoe sizes in shop as string e.g. "2 3 4 5 6 8 7 6 5 18"
shoes_list = [int(number) for number in shoes.split()]
shoe_counter = C(shoes_list)

N = int(input("N: "))
customer_purchase_desires = []
for c in range(N):
    customer_purchase_desires.append(input(f"Customer {c+1}: ").split())

print(shoe_counter)
print(customer_purchase_desires)

# Calculation
sales = 0
for c in range(N):
    desired_size = int(customer_purchase_desires[c][0])
    if shoe_counter[desired_size] > 0:
        shoe_counter[desired_size] -= 1
        sales += int(customer_purchase_desires[c][1])
        
    else:
        pass
print(sales)
