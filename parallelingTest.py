import multiprocessing
import time

def factorial(n):
    result = 1
    for i in range(1, n + 1):
        result *= i
    return n, result

def parallel_factorial_calculator(numbers):
    if not numbers:
        return []

    # Using a context manager to ensure proper cleanup of the pool
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        # Map the factorial function to the numbers
        results = pool.map(factorial, numbers)

    return results


# Example usage of the function
if __name__ == "__main__":
    numbers = [100000, 100001, 100002, 100003, 100004, 100005, 100006, 100007, 100008, 100009, 100010]
    results = parallel_factorial_calculator(numbers)
    for result in results:
        print(result)
