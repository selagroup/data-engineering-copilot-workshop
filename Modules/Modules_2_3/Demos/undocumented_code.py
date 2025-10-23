
import numpy as np

def fibonacci_matrix(n):
    """
    Calculates the nth Fibonacci number using matrix exponentiation.
    This function leverages the property that the nth Fibonacci number can be computed
    by raising the Fibonacci Q-matrix ([[1, 1], [1, 0]]) to the (n-1)th power and taking
    the top-left element of the resulting matrix.
    Args:
        n (int): The position in the Fibonacci sequence to compute. Must be a non-negative integer.
    Returns:
        int: The nth Fibonacci number.
    Examples:
        >>> fibonacci_matrix(0)
        0
        >>> fibonacci_matrix(1)
        1
        >>> fibonacci_matrix(10)
        55
    Notes:
        - Requires NumPy to be imported as np.
        - Efficient for large values of n due to logarithmic time complexity.
    """
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