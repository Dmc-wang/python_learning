"""
任务1.1:加载数据（就像打开案件卷宗）
    目标:把CSV数据搬进Python,确认数据成功加载

    思路步骤：
    导入Pandas库(这是你处理数据的瑞士军刀)
    用Pandas读取CSV文件,指定编码为utf-8(防止中文乱码)
    把读取结果存到一个变量(通常叫df,代表DataFrame)
    验证:打印出数据的行数和列数,确认和原始CSV一致(200行,8列)
    
    思考要点：
    如果加载时报错,可能是路径不对、编码问题,或者CSV格式不标准
    加载后第一件事：检查形状，确认数据没有 truncated(被截断)
"""
import pandas 

df = pandas.read_csv('~/python_learning/python_learning/S01_dataFX/data/raw/demo_ecommerce.csv', encoding = 'utf-8')
# 查看前5行
print(f"前5行数据:\n{df.head(5)}")

# 查看数据维度
print(f"数据维度:\n{df.shape}")

# 查看数据列名
print(f"数据列名:\n{df.columns}")



