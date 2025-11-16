"""
    示例程序 1：BMI 计算器（变量 + 输入输出）
    requirements:
    输入身高、体重
    输出 BMI = 体重 / 身高²
    判断体型（偏瘦/正常/偏胖）
"""
height = float(input("请输入你的身高(m):"))
weight = float(input("请输入你的体重(kg):"))
bmi = weight / (height  ** 2)
print(f"BMI的值:{bmi:.2f}")
if bmi < 18.5:
    print("体型:偏瘦")
elif bmi < 24:
    print("体型:正常")
else:
    print("体型:偏胖")