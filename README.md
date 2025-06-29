# Theoretical equivalence of functional and imperative programming
This project serves (somewhat) as a constructive proof that imperative and functional programming paradigms are computationally equivalent.
We take Lambda Calculus as a representative of functional languages, and Magma + Python as stand-ins for imperative languages.

## Magma Language
Magma is a simplistic Turing complete python-like language. It supports positive integers, booleans and arrays (of unbounded size). The following code examples should give a good idea of the syntax available:
```
n = 15
fibo = 1..n

fibo @ 1 = 1

for i in 2..n
    fibo @ i = (fibo @ (i-1)) + (fibo @ (i-2))
```

```
i = 1
repeat 100
    if i % 15 == 0
        print [true, false]
    elif i % 3 == 0
        print [true]
    elif i % 5 == 0
        print [false]
    else
        print i
i = i + 1
```

```
target = 10

i = 0
f = 1
while f < target
    i = i + 1
    f = 1
    for j in 1..i
        f = f * j
print i
```

## Compilation
Magma code is compiled into lambda calculus by converting each atomic expression (variable assignment, print, array assignment) into a lambda function taking in as input a state <M, P> where M represents a list of variables (each variable name becomes an index in the list) and P the list of values printed out.
Then, code blocks are handled inductively by getting the state function of each line of code it contains, composing them together then wrapping with code relevant for the type of control flow.

*Details will be added at a later date*

## Interpretation
Lambda code is then interpreted in python using the leftmost-outermost reduction strategy, which necessarily terminates in the case of normal forms (which is the case for code generated by the compiler) as a corollary of the Church-Rosser and Standardization theorems.

## Context
This project was made in the context of the TIPE in french preparatory schools. The article I wrote for it (in french) is included in the project. (An english version will be made eventually)