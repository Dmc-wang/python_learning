"""
任务1.2:初步观察（像侦探第一眼扫视现场）
    目标：快速了解数据长什么样，有哪些"嫌疑人"（问题）

    思路步骤：
        看头部:展示前5-10行,观察：
            列名是否正确读取
            数据内容是否符合预期(比如amount应该是数字)
            有没有明显的格式问题（日期、文本混合）

        看尾部:展示后5行,观察:
            数据结尾是否有空行或异常值
            索引是否连续

        看信息摘要：获取每个字段的"档案":
            数据类型:object(文本)、int64(整数)、float64(小数)等
            非空值数量:如果少于200,说明有缺失值
            内存占用：了解数据规模

    思考要点：
        哪些列应该是数值型但被识别成了文本？（后续需要转换）
        哪些列有空值?(Non-Null Count < 200)
        category列应该是分类数据,却被当成object,这正常吗?
"""

import pandas

df = pandas.read_csv('~/python_learning/python_learning/S01_dataFX/data/raw/demo_ecommerce.csv', encoding = 'utf-8')

# 查看前10行
print(f"前10行数据:\n{df.head(10)}")

# 查看后5行
print(f"后5行数据:\n{df.tail(5)}")

# 查看数据摘要信息
print(f"数据摘要信息:\n{df.info()}")