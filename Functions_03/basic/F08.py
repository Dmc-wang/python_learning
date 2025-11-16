#F8: 返回列表中最大值与最小值
def get_min_max(nums: list) -> tuple[int, int]:
    if not nums:
        raise ValueError("list cannot be empty")
    return  min(nums), max(nums)

n = [1, 2, 3, 4, 5]
print(get_min_max(n))
print(get_min_max(n)[0])