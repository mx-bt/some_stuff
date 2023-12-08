import numpy as np

def ask_user(a, b):
    """Get answer from user: a*b = ?"""
    answer = int(input(f"{a}*{b}= "))
    return answer
def points(a, b, answer_given):
    """Check answer. Correct answer gives 1 point, else zero"""
    true_answer = a*b
    if answer_given == true_answer:
        print("Correct!")
        return 1
    else:
        print(f"Sorry! Correct answer was: {true_answer}")
    return 0

print("*** Welcome to the times tables test! ***")
print("To stop: ctrl-c")
N = 10
NN = N*N
score = 0
index = list(range(0, NN, 1))
np.random.shuffle(index) # randomize order of integers in index
for i in range(0, NN, 1):
    a = index[i]//N + 1
    b = index[i]%N + 1
    try:
        user_answer = ask_user(a, b)
    except KeyboardInterrupt:
        print("Ok, you want to stop!")
        break
    except ValueError:
        print("You must give a valid number!")
        continue # jump to next loop iteration
    score = score + points(a, b, user_answer)

    print(f"Your score is now: {score}")
print(f"Finished! Your final score: {score} (max: {N*N})")