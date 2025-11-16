# T2：寻找元组中第二大的数字
# 例如 (3, 6, 1, 8, 2) → 输出 6

t = input("请输入一个元组（如：3,6,1,8,2）：").split(",")
nums = [int(x) for x in t]

max_num = nums[0]
second_max = None

for n in nums:
    if n > max_num:
        second_max = max_num
        max_num = n
    elif second_max is None or (n > second_max and n != max_num):
        second_max = n

print("元组中第二大的数字：", second_max)