# F4：实现一个求列表中所有偶数的函数
# 输入列表 → 输出：只包含偶数的新列表

def get_even_numbers(lst):
    # 用列表推导式选出所有偶数
    even_list = [x for x in lst if x % 2 == 0]
    return even_list

nums = input("请输入一组数字，用空格或逗号分隔：").replace(',', ' ').split()
nums = [int(x) for x in nums]
result = get_even_numbers(nums)
print("列表中的所有偶数为：", result)