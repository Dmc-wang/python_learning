#L2：列表去重 + 排序
#输入 [3,1,2,3,4,2] → 输出 [1,2,3,4]
lst = (input("请输入一组数字，用逗号或空格分隔：")
       .replace(',', ' ').split())
nums = [int(x) for x in lst]
print("原始列表",nums)

#去重
#unique_nums = set(nums)
unique_nums = []
for i in nums:
    if i not in unique_nums:
        unique_nums.append(i)
print("去重",unique_nums)

#排序
#result = sorted(unique_nums)
result = unique_nums
for i in range(len(result)):
    for j in range(i+1, len(result)):
        if result[i] > result[j]:
            result[i], result[j] = result[j], result[i]
print("排序",result)