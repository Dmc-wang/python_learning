#判断一个整数是奇数还是偶数
x=int(input("请输入一个整数:"))
if x % 2 == 0:
    print(x,"是偶数")
    print(f"{x}是偶数")
else:
    print(x,"是奇数")
    print(f"{x}是奇数")
