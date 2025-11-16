#输入分数，输出等级 A/B/C/D
score=int(input("请输入你的分数（0-100）:"))
if score >= 90:
    print("你的等级是A")
elif score >= 80:
    print("你的等级是B")
elif score >= 60:
    print("你的等级是C")
else:
    print("你的等级是D")
