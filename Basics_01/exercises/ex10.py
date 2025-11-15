#输入列表，输出最大值与最小值
lst = input("请输入一组数字，用空格符分隔：").split()
print(lst)
nums = [float(x) for x in lst]
print(nums)
max_num=nums[0]
min_num=nums[0]

for i in nums:
    if i>max_num:
        max_num=i
    if i<min_num:
        min_num=i
print(f"最大值为：{max_num}")
print(f"最小值为：{min_num}")

