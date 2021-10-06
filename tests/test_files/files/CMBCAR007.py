str1 = "Race"
str2 = "Care"

# convert both the strings into lowercase
str1 = str1.lower()
str2 = str2.lower()

# check if length is same
if(len(str1) == len(str2)):

    # sort the strings
    sorted_str1 = sorted(str1)
    sorted_str2 = sorted(str2)

    # if sorted char arrays are same
    if(sorted_str1 == sorted_str2):
        print(str1 + " and " + str2 + " are anagram.")
    else:
        print(str1 + " and " + str2 + " are not anagram.")

else:
    print(str1 + " and " + str2 + " are not anagram.")

# Similar code:
num = 1234
reversed_num = 0

while num != 0:
    digit = num % 10
    reversed_num = reversed_num * 10 + digit
    num //= 10

print("Reversed Number: " + str(reversed_num))

# Program to check if a number is prime or not

num = 29

# To take input from the user
#num = int(input("Enter a number: "))

# define a flag variable
flag = False

# prime numbers are greater than 1
if num > 1:
    # check for factors
    for i in range(2, num):
        if (num % i) == 0:
            # if factor is found, set flag to True
            flag = True
            # break out of loop
            break

# check if flag is True
if flag:
    print(num, "is not a prime number")
else:
    print(num, "is a prime number")

# Add base file code (should be ignored in report)


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


print(file_len("my_file.txt"))
