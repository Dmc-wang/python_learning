#异常处理结构
try:
    age = int(input("请输入你的年龄: "))
    print(f"你输入的年龄是: {age}")
except ValueError:
    print("输入无效！请输入数字。")
finally:
    print("done")
