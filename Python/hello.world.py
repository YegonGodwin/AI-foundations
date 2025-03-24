x = int(input("Enter num1: "))
y = int(input("Enter num2: "))

sum_total = x + y
if (sum_total >= 50):
    print("Give the ticket")
elif (sum_total < 50 and sum_total > 40):
    print("Give temporary ticket")
else:
    print("Do not give out any ticket")