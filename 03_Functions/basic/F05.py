# F5：实现一个“可变参数”函数，计算任意数量的数字平均值
# 例如：
# avg(1,2,3,4) → 2.5
# （用 *args）

def avg(*args):
    if len(args) == 0:
        return 0
    return sum(args) / len(args)

# 主程序示例
print(avg(1, 2, 3, 4))       # 输出：2.5
print(avg(10, 20))           # 输出：15.0
print(avg())                 # 输出：0