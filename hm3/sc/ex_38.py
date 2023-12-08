"""Exercise 3.8: Game 21"""
#	 game_21.py

import numpy as np
import random as rd

n_players = int(input("Enter number of players: "))
players = []
for p in range(n_players):
	name = input(f"Enter player {p+1}'s name: ")
	players.append(name)
	print(f"Welcome, {players[p]}")



results = []
for n in players:
	cont = "y"
	answer = input(f"{n},enter y to draw your numbers: ")
	if answer == "y" and cont=="y":
		draw_sum = 0
		rd.seed(123) # for testing
		while cont=="y":
			draw = []
			card = rd.randint(0,10)
			draw.append(card)
			draw_sum += card
			print("Your draw: ",draw)
			print("Current sum: ",draw_sum)
			if draw_sum > 21:
				print(f"{n}, RIP, you're out")
				results.append(0)
				cont="n"
			else:
				cont = input("You want to draw again?(y/n): ")
				if cont == "y":
					print("Next draw...")
				else:
					results.append(draw_sum)
					cont = "n"
	else:
		pass

print("===========================")
try:
	for p in range(n_players):
		print(f"Score of {players[p]}: {results[p]}")
except IndexError:
	print("Not everyone played")


