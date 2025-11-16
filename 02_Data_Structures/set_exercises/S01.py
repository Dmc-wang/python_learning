# S1：求两个列表的交集
# 输入两个列表 → 输出共同元素（使用 set）

# lst1 = input("请输入第一个列表，用空格分隔：").split()
# lst2 = input("请输入第二个列表，用空格分隔：").split()

lst1 = [1, 2, 3, 4, 5]
lst2 = [4, 5, 6, 7, 8]

lst1_s = set(lst1)
lst2_s = set(lst2)

intersection = lst1_s & lst2_s

print(intersection)