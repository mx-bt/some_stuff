#   Revisit 4.13: Fit sines to Straight Line
import numpy as np
import matplotlib.pyplot as plt

t_test = [-np.pi/2,np.pi/4]
b_test = [4,-3]

def sinesum(t,b): # t=time coordinates, b=coefficients b_n
    t = np.array(t)
    b = np.array(b)
    SN_t = float()
    for n in range(len(b)):
        SN_t += b[n]*np.sin((n+1)*t)
    return SN_t

# print(sinesum(t_test,b_test))

def test_sinesum():
    t_test = [-np.pi/2,np.pi/4]
    b_test = [4,-3]
    sinesum_tt = sinesum(t_test,b_test)
    sinesum_hand = np.array([4*np.sin(1*-np.pi/2)+(-3)*np.sin(2*-np.pi/2),4*np.sin(1*(np.pi/4))+(-3)*np.sin(2*np.pi/4)])
    print(sinesum_tt)
    print(sinesum_hand)
    return sinesum_hand, sinesum_tt

# test_sinesum()

def plot_compare(f, b=np.ones_like(range(10)), M=500):
    t_vals = np.array(np.linspace(-np.pi,np.pi,M))
    y_f = f(t_vals)
    y_SNt = sinesum(t_vals,b)

    plt.figure(figsize=(8, 6))

    # Plot the first function
    plt.plot(t_vals, y_f, label='Original function f(t)', color='blue')
    plt.plot(t_vals, y_SNt, label='Sum of sines SN(t)', color='green')

    # Display the x and y axes
    plt.axhline(0, color='black',linewidth=0.5)
    plt.axvline(0, color='black',linewidth=0.5)
    # Set axis labels and title
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('plot_compare(f, N, M)')
    # Add a legend
    plt.legend()
    plt.grid()  # Add grid lines if desired
    plt.show()

def error(b,f,M=500):
    t_vals = np.array(np.linspace(-np.pi,np.pi,M))
    y_f = f(t_vals)
    y_SNt = sinesum(t_vals,b)
    error_E = 0

    for value_pair_index in range(len(t_vals)):
        error_E += (y_f[value_pair_index]-y_SNt[value_pair_index])**2
    error_E = np.sqrt(error_E)
    print("Error= ",error_E)
    return error_E


# plot_compare(f_tt, N, M=500)    
# error(np.ones_like(range(N)),f_tt)

def trial(f,N):
    print("Experiment start")
    print("")
    
    cont = True
    while cont == True:
        b_values = []
        for bs in range(N):
            print("")
            new_b = float(input(f"Enter b #{bs+1}: "))
            b_values.append(new_b)
        b_values = np.array(b_values)

        plot_compare(f, b_values)
        print(error(b_values,f))
        print("")

        print("To continue answer with Yes,")
        print("To quit, enter anything.")
        cont_statement = input("Do you wish to continue?...")
        if cont_statement == "Yes":
            continue
        else:
            cont = False
            break




N = 100

# trial(f_tt,3)



def automated_search(f):
    best_bees = np.array([])
    smallest_E = np.inf
    search_range = np.linspace(-5,5,21)

    for b1 in search_range:
        for b2 in search_range:
            for b3 in search_range:
                temp_E = error(np.array([b1,b2,b3]),f)
                if smallest_E > temp_E:
                    smallest_E = temp_E
                    best_bees = np.array([b1,b2,b3])
                else:
                    continue

    t_vals = np.array(np.linspace(-np.pi,np.pi,1000))
    y_f = f(t_vals)
    y_SNt = sinesum(t_vals,best_bees)

    plt.figure(figsize=(8, 6))

    # Plot the first function
    plt.plot(t_vals, y_f, label='Original function f(t)', color='blue')
    plt.plot(t_vals, y_SNt, label='Sum of sines SN(t)', color='green')

    # Display the x and y axes
    plt.axhline(0, color='black',linewidth=0.5)
    plt.axvline(0, color='black',linewidth=0.5)
    # Set axis labels and title
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('plot_compare(f, N, M)')
    # Add a legend
    plt.legend()
    plt.grid()  # Add grid lines if desired
    plt.show()


    return best_bees

f_tt = lambda x: x/np.pi*5
print(automated_search(f_tt))
