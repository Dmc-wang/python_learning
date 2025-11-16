#D2：学生成绩字典处理
# 输入：{"Tom": 90, "Bob": 80, "Alice": 95}
# 输出最高分学生姓名与分数
scores=eval(input("请输入学生成绩字典，如{“Tom”:90,“Bob”:80}:"))
print(scores)

max_name=None
max_score=None

for name,score in scores.items():
    if max_score is None or score > max_score:
        max_name=name
        max_score=score

print("最高分学生",max_name)
print("最高分",max_score)