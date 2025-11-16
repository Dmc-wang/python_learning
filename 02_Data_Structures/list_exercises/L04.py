#L4（挑战）：合并两个已排序列表
#[1,3,5] + [2,4,6] → [1,2,3,4,5,6]

lst1 = input("请输入第一组数字，用空格分隔：").split()
lst1_num = [int(x) for x in lst1]
lst1_uni = set(lst1_num)
lst1_sort = sorted(lst1_uni)
print("第一组：",lst1_sort)

lst2 = input("请输入第一组数字，用空格分隔：").split()
lst2_num = [int(x) for x in lst2]
lst2_uni = set(lst2_num)
lst2_sort = sorted(lst2_uni)
print("第二组：",lst2_sort)

#双指针归并
# i, j = 0, 0
# result = []
# while i < len(lst1_sort) and j < len(lst2_sort):
#     if lst1_sort[i] <= lst2_sort[j]:
#         result.append(lst1_sort[i])
#         i += 1
#     else:
#         result.append(lst2_sort[j])
#         j += 1
#
# #处理剩余元素
# result.extend(lst1_sort[i:])
# result.extend(lst2_sort[j:])

#heapq.merge()
import heapq
result = list(heapq.merge(lst1_sort, lst2_sort))
print("合并后两个已排序列表",result)




