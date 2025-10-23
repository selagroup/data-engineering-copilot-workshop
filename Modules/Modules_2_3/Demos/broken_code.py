# This code should calculate the average of a list of numbers

def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

def main():
    numbers_list = [1, 2, 3, 4, 5]
    result = calculate_average(numbers_list)
    print("The average is: " + str(result)) 
    
    # Example loop, define count and unknown_variable if needed
    # for i in range(count):
    #     print(unknown_variable)

if __name__ == "__main__":  
    main()