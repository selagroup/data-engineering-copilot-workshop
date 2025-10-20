
def find_duplicates(input_list):
    # Unoptimized way to find duplicates in a list
    duplicates = []
    for i in range(len(input_list)):
        for j in range(len(input_list)):
            # Inefficient double loop with unnecessary comparisons
            if i != j and input_list[i] == input_list[j] and input_list[i] not in duplicates:
                duplicates.append(input_list[i])
                # Unnecessary list conversion and string operations
                print("Found duplicate: " + str(list([input_list[i]])))
    
    # Inefficient way to sort results
    for i in range(len(duplicates)):
        for j in range(len(duplicates)-1):
            if duplicates[j] > duplicates[j+1]:
                duplicates[j], duplicates[j+1] = duplicates[j+1], duplicates[j]
    
    return duplicates

# Test the function with a sample list
test_list = [2, 3, 1, 5, 2, 4, 3, 6, 5, 8, 1, 0]
result = find_duplicates(test_list)
print("Final result:", result)