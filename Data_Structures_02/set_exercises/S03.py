# S3：利用集合实现列表去重
# 输入 [1, 1, 2, 3, 3] → 输出 [1, 2, 3]

lst1 = [1, 1, 2, 3, 3]
print(lst1)

lst1_s = set(lst1)
print(lst1_s)

lst2 = list(lst1_s)
print(lst2)