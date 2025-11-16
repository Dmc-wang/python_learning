# F1：实现一个判断素数的函数
# 输入 n → 返回 True / False

def is_prime(num):
    if num < 2:
        return False
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True

# 主程序部分
n = int(input("请输入一个整数："))
if is_prime(n):
    print(f"{n} 是素数。")
else:
    print(f"{n} 不是素数。")