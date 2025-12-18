"""
任务1.3:统计画像（给每列数据画个肖像）
    目标：了解数值列的分布，文本列的类别

    思路步骤：
        A. 数值列(age, amount):
            查看描述性统计：均值、标准差、最小值、四分位数、最大值
        思考：
            age均值是否合理?(正常应在20-50之间)
            amount最大值是否异常?(比如超过10000可能有问题)
            标准差大说明数据分散，小说明集中

        B. 文本/分类列(gender, category, city):
            查看每个类别的唯一值数量和具体列表
            统计每个类别的出现频次(用value_counts())
        思考：
            category应该只有几个固定值,如果很多就要检查是否有拼写错误
            city有多少个城市?是否有空白或异常值?
            gender是否只有Male和Female?有没有其他奇怪的?
"""
import pandas as pd

# 读取数据
df = pd.read_csv('~/python_learning/python_learning/S01_dataFX/data/raw/demo_ecommerce.csv', encoding = 'utf-8')

# A. 数值列画像
print("数值列描述性统计：")
numeric_cols = ['age', 'amount']
for col in numeric_cols:
    print(f"\n列: {col}")
    print(df[col].describe(include = 'all'))

# B. 文本/分类列画像
categorical_cols = ['gender', 'category', 'city']
print("文本/分类列画像：")

for col in categorical_cols:
    print(f"\n列: {col}")
    print(f"\n{col}列有多少不同的值:{df[col].nunique()}")
    print(f"\n{col}列唯一值:\n{df[col].unique()}")
    print(f"\n{col}列值频次:\n{df[col].value_counts()}")

