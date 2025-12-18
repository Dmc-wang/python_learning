"""
任务1.5:业务洞察(数据在讲什么故事?)
目标：回答几个简单但重要的问题，验证数据是否"说得通"
    思路步骤:
        最简单的聚合分析:
            哪个category的订单数量最多?(用value_counts)
            哪个category的总销售额最高?(按category分组求和amount)
            哪个城市的订单最多?

        初步关联观察：
            男性和女性的平均消费金额有差异吗?(按gender分组算amount均值)
            年龄和消费金额有关系吗?(试着画个简单的散点图，虽然你现在可能只想思路)
        
        时间维度：
            观察purchase_date的早晚顺序,确认数据是按时间排序还是乱序
            最早和最晚的日期分别是什么时候?
"""
import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
df = pd.read_csv('~/python_learning/python_learning/S01_dataFX/data/raw/demo_ecommerce.csv', encoding = 'utf-8')

# 最简单的聚合分析
# 哪个category的订单数量最多?
category_counts = df['category'].value_counts()
print("各类别订单数量:\n", category_counts)

most_orders_category = category_counts.idxmax()
print(f"订单数量最多的类别: {most_orders_category}，订单数量: {category_counts.max()}")    

# 哪个category的总销售额最高?
category_sales = df.groupby('category')['amount'].sum()
print("各类别总销售额:\n", category_sales)

highest_sales_category = category_sales.idxmax()
print(f"总销售额最高的类别: {highest_sales_category}，总销售额: {category_sales.max()}")    

# 哪个城市的订单最多?
city_counts = df['city'].value_counts()
print("各城市订单数量:\n", city_counts)

most_orders_city = city_counts.idxmax()
print(f"订单数量最多的城市: {most_orders_city}，订单数量: {city_counts.max()}")   

# 初步关联观察
# 男性和女性的平均消费金额有差异吗?
gender_avg_amount = df.groupby('gender')['amount'].mean()
print("各性别平均消费金额:\n", gender_avg_amount)

# 年龄和消费金额有关系吗?
plt.scatter(df['age'], df['amount'], alpha=0.5)
plt.title('年龄 vs 消费金额')
plt.xlabel('年龄')
plt.ylabel('消费金额')
plt.show()

# 时间维度
df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors = 'coerce')
is_sorted = df['purchase_date'].is_monotonic_increasing
print(f"数据按时间排序: {is_sorted}")
earliest_date = df['purchase_date'].min()
latest_date = df['purchase_date'].max()
print(f"最早的购买日期: {earliest_date}")
print(f"最晚的购买日期: {latest_date}") 

