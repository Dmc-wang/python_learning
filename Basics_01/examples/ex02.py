"""
    示例程序 2：猜数字游戏（流程控制 + 循环）
    requirements:
    程序随机生成 1–100
    用户猜数字
    提示高了/低了
    直到猜对

"""

#方法一：使用 while 循环
# import random
#
# number=random.randint(1,100)
# guess=None
#
# while guess!=number:
#     guess = int(input("请输入你猜的数字（1-100）："))
#     if guess < number:
#         print("太低了")
#     elif guess > number:
#         print("太高了")
#     else:
#         print("猜对了")

#方法二：使用无限循环并计数尝试次数
import random

number = random.randint(1, 100)
attempts = 0

while True:
    guess = int(input("请输入你猜的数字（1-100）："))
    attempts += 1
    if guess < number:
        print("太低了！")
    elif guess > number:
        print("太高了！")
    else:
        print(f"恭喜你，猜对了！共尝试了 {attempts} 次。")
        break