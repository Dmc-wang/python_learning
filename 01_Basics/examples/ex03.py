"""
    示例程序 3：学生成绩管理（列表 + 循环）
    requirements:
    输入 5 个成绩
    输出：
    最高分
    最低分
    平均分
    BONUS：成绩排序
"""
#score_s = input("请输入5个成绩，空格分开：").split()
score_num=[]
for i in range(5):
    score = float(input(f"请输入第{i+1}个成绩："))
    score_num.append(score)

max_score = max(score_num)
min_score = min(score_num)
average_score = sum(score_num) / len(score_num)
sorted_score = []
temp_score = score_num[:]

while temp_score:
    min_val=temp_score[0]
    for i in temp_score:
        if i<min_val:
            min_val=i
    sorted_score.append(min_val)
    temp_score.remove(min_val)
"""
# 方法1：内置排序（推荐）
scores = [85, 92, 78, 95, 88]
sorted_scores = sorted(scores)  # 返回新列表
print(sorted_scores)  # [78, 85, 88, 92, 95]
# scores 原列表不变

# 方法2：原地排序
scores.sort()  # 直接修改原列表
print(scores)  # [78, 85, 88, 92, 95]

# 方法3：降序排列
sorted_scores_desc = sorted(scores, reverse=True)
print(sorted_scores_desc)  # [95, 92, 88, 85, 78]

** 总结**：理解这个算法很好，但实际
开发中请直接用 sorted() 或 .sort()！

"""

print(f"最高分：{max_score}")
print(f"最低分：{min_score}")
print(f"平均分：{average_score}")
print(f"成绩排序（从低到高）：{sorted_score}")






