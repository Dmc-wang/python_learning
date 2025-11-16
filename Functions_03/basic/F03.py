# F3：实现一个求斐波那契数列的函数
# 输入 n → 输出第 n 个斐波那契数
# 例如 F(6) = 8
# （你可以选择递归或循环）

# def fibonacci_recursive(n):
#     if n == 0 or n == 1:
#         return n
#     return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)

def fibonacci_recursive(n):
    if n == 0:
        return 0
    if n == 1:
        return 1

    a,b = 0,1
    for _ in range(2,n+1):
        c = a + b
        a = b
        b = c
    return b

num = int(input("请输入 n（要求第 n 个斐波那契数）："))
print(f"第 {num} 个斐波那契数为：{fibonacci_recursive(num)}")