#   Exercise 4.7: Average of Integers
#   average_1_to_N.py

N = 0
while N <= 1:
	N = int(input("Choose an integer greater than 1: "))

def avg_of_integers(integer):
	sum = 0
	for i in range(integer):
		sum += i+1
	av = sum/integer
	print(f"The average of all integers between {1} and {integer} is {round(av,3)}")
	return av

avg_of_integers(N)