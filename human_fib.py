def fib(n):
    if n <= 1: return n
    # recursion feels elegant even if slow
    return fib(n-1) + fib(n-2)  # nostalgic
    # TODO: memoize later
