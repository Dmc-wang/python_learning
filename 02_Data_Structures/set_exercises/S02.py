# S2：求并集和差集
# 两组数据 → 输出并集 / 交集 / 差集

lst1 = [1, 2, 3, 4, 5]
lst2 = [4, 5, 6, 7, 8]

set1 = set(lst1)
set2 = set(lst2)

union = set1 | set2       # 并集
intersection = set1 & set2  # 交集
difference = set1 - set2    # 差集（只在 set1 中）

print("并集：", union)
print("交集：", intersection)
print("差集（第一组 - 第二组）：", difference)

lst3=list(union)
lst4=list(intersection)
lst5=list(difference)

print("并集：", lst3)
print(lst3[0])
print("交集：", lst4)
print("差集（第一组 - 第二组）：", lst5)