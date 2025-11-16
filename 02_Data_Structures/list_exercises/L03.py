#L3：统计列表中某个数字出现次数
#例如统计 3 出现几次。

# list0 = [1, 1, 3, 2, 2, 4, 4, 5, 5, 4]
# sta_num = 4
# count = 0
# for i in list0:
#     if sta_num == i:
#         count += 1
# print(count)

lst = input("请输入一组数字，用空格分隔：").split()
nums = [int(x) for x in lst]
target = int(input("请输入要统计的数字："))
count = 0

for n in nums:
    if n == target:
        count += 1

print(f"{target} 在列表中出现了 {count} 次。")