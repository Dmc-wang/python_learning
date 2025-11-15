#求列表中的最大、最小、平均值
#输入一个列表，输出最大值、最小值、平均值。
lit = input("请输入一组数字，用空格符分隔：").split()
nums = [float(x) for x in lit]

max_num = max(nums)
min_num = min(nums)
average_num = sum(nums) / len(nums)

print("max=", max_num)
print("min=", min_num)
print("average=", average_num)

