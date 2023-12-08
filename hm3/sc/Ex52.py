#   Exercise 5.2: Exception Handling: Divisions in a Loop

N = 4
for tries in range(N):
    try:
        a = float(input("Enter a real number a: "))
        b = float(input("Enter a real number b: "))
        print("Result: ",a/b)
        break
    except  ValueError:
        print("pls enter an actual number, not a string or whatever")
    except ZeroDivisionError:
        print("Albert Einstein once said: one cannot divide by fucking zero you ridiculous retard")
        pass
    except KeyboardInterrupt:
        print("oki maybe next time")
        break







