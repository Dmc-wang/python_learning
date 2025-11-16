#求 1–100 的累加和
"""
    sum1 = 0
    i = 0
    while i < 100:
        i += 1
        sum1 += i
    print(f"1–100 的累加和 = {sum1}")
"""

total = 0
for i in range(1,101):  #1 <= i <101
    total += i
print("1-100的累加和",total)