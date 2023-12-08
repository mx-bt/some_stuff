def fibo(N):
    if N == 1:
        fn = [1]
        return fn
    elif N == 2: 
        fn = [1,1]
        return fn
    else:
        fn = [1,1]
        for n in range(N-2):
            fn.append(fn[n]+fn[n+1])
        return fn

def converging_ratio(N):
    import numpy
    golden_ratio = (1+numpy.sqrt(5))/2
    gr = []
    for n in range(N):
        gr.append(golden_ratio)
    gr = numpy.array(gr)
    
    F = fibo(N)
    fr = []
    for n in range(N-1):
        r = F[n+1]/F[n]
        fr.append(r)
    fr = numpy.array(fr)
    
    e = []
    for i in range(N-1):
        e.append(fr[i]-gr[i])
    e = numpy.abs(numpy.array(e))
    """
    print("golden: ",numpy.round(gr,2))
    print("fibon.: ",numpy.round(fr,2))
    print("error: ",numpy.round(e,2))"""
    return gr, fr, e

#print(converging_ratio(10))

# converging_ratio(5)
# [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181, 6765]

def compute_rates(N):
    import numpy
    if N < 3:
        print("Fibonacci series must be longer than 3 elements to calculate q")
        return numpy.nan
    else:
        e = converging_ratio(N)[2]
        print(e)
        #print(numpy.log(e))
        print(numpy.log(e))
        q = (numpy.log(e[N-2]/e[N-3]))/(numpy.log(e[N-3]/e[N-4]))
        return q

print(compute_rates(15))
