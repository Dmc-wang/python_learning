import random

# 功能：随机返回一个 1 到 100 之间（含） 的整数。
def rand_int():
    return random.randint(1,100)

# 功能：从列表 lst 中随机选一个元素返回。
def choice_item(lst):
    return random.choice(lst)