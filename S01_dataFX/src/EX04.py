"""
任务1.4:质量检查(寻找"犯罪证据")
    目标：主动发现问题，而不是被动等待

    思路步骤：
        重复值侦查：
            检查是否有完全一致的行(用户ID、商品、金额等都相同)
            思考：重复记录是真实发生(用户真的买了两次)，还是数据录入错误？
        缺失值地图：
            统计每列缺失值的数量和比例
            重点观察:age、category、city这三列
            思考:缺失是随机的,还是有某种模式?(比如某个城市的记录都缺age)
        异常值初探：
            在amount列,找出超出常识范围的值(比如负数,或超过5000)
            在age列,找出小于18或大于80的值(可能是录入错误)
            在purchase_date列,检查日期范围是否合理(应在2024年内)
"""
import pandas as pd

# 读取数据
df = pd.read_csv('~/python_learning/python_learning/S01_dataFX/data/raw/demo_ecommerce.csv', encoding = 'utf-8')

# 重复值侦查
duplicate_rows = df[df.duplicated()]
print(f"重复行数: {duplicate_rows.shape[0]}")
if not duplicate_rows.empty:
    print(f"重复行数据:\n{duplicate_rows}")

# 缺失值地图
missing_values = df.isnull().sum()
missing_percentage = (missing_values / len(df)) * 100
missing_summary = pd.DataFrame({'缺失值数量': missing_values, '缺失值比例(%)': missing_percentage})
print("缺失值统计:\n", missing_summary)

# 异常值初探
# 检查amount列
abnormal_amounts = df[(df['amount'] < 0) | (df['amount'] > 5000)]
print(f"异常amount值行数: {abnormal_amounts.shape[0]}")
if not abnormal_amounts.empty:
    print(f"异常amount值数据:\n{abnormal_amounts}")

# 检查age列
abnormal_ages = df[(df['age'] < 18) | (df['age'] > 80)]
print(f"异常age值行数: {abnormal_ages.shape[0]}")
if not abnormal_ages.empty:
    print(f"异常age值数据:\n{abnormal_ages}")

# 检查purchase_date列
df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors = 'coerce')
abnormal_dates = df[(df['purchase_date'] < '2024-01-01') | (df['purchase_date'] > '2024-12-31')]
print(f"异常purchase_date值行数: {abnormal_dates.shape[0]}")
if not abnormal_dates.empty:
    print(f"异常purchase_date值数据:\n{abnormal_dates}")
