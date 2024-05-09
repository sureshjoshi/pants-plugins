import time

def fib() -> None:
    def fib(n: int) -> int:
        if n <= 1:
            return n
        return fib(n - 2) + fib(n - 1)

    start_time = time.time()
    fib(34)
    print(f"Calculating fibs took {time.time() - start_time} seconds")
