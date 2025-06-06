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