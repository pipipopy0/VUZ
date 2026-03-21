def rec(i):
    i = i + 1
    print(i)
    if i < 10:
        rec(i)

rec(0)