# T1：元组解包
# 输入元组 (name, age, city)，格式化输出：“XX 今年 XX 岁，住在 XX”。

t = input("请输入一个元组（如：Tom,18,Beijing）：").split(",")
name, age, city = t
print(f"{name} 今年 {age} 岁，住在 {city}")