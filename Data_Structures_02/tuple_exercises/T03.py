# T3：将列表转换为元组，并输出长度与类型
# 输入 [1,2,3]
lst = input("请输入一个列表，用逗号或空格分隔（如：1,2,3）：").replace(',', ' ').split()
nums = [int(x) for x in lst]
print(nums)
print("列表内容：", nums)
print("列表长度：", len(nums))
print("列表类型：", type(nums))
print(nums[0])

t = tuple(nums)
print("元组内容：", t)
print("元组长度：", len(t))
print("元组类型：", type(t))
print(t[0])