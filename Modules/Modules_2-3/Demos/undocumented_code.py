
import numpy as np

def fibonacci_matrix(n):
    def matrix_mult(A, B):
        return np.dot(A, B)

    def matrix_pow(M, power):
        result = np.identity(len(M), dtype=int)
        base = M

        while power > 0:
            if power % 2 == 1:
                result = matrix_mult(result, base)
            base = matrix_mult(base, base)
            power //= 2

        return result

    if n <= 0:
        return 0
    elif n == 1:
        return 1

    F = np.array([[1, 1], [1, 0]], dtype=int)
    result = matrix_pow(F, n - 1)
    return result[0][0]

# Example usage:
n = 10
print(f"Fibonacci number {n} is {fibonacci_matrix(n)}")