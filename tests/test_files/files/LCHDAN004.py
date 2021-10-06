
# Unique code
def get_permutation(string, i=0):

    if i == len(string):
        print("".join(string))

    for j in range(i, len(string)):

        words = [c for c in string]

        # swap
        words[i], words[j] = words[j], words[i]

        get_permutation(words, i + 1)


print(get_permutation('yup'))

# Similar code:
list_1 = [1, 2, 3, 4]
list_2 = ['a', 'b', 'c']

for i, j in zip(list_1, list_2):
    print(i, j)

num = 1234
reversed_num = 0

while num != 0:
    digit = num % 10
    reversed_num = reversed_num * 10 + digit
    num //= 10

print("Reversed Number: " + str(reversed_num))


# Add base file code (should be ignored in report)
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


print(file_len("my_file.txt"))
