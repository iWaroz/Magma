n = 15
fibo = 1..n

fibo @ 1 = 1

for i in 2..n
    fibo @ i = (fibo @ (i-1)) + (fibo @ (i-2))