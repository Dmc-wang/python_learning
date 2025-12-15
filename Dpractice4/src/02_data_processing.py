# src/02_data_processing.py
"""
学习目标：
1. pandas核心操作：筛选、分组、聚合
2. lambda函数和apply方法
3. 链式调用（方法链）
4. 数据清洗技巧
"""

import pandas as pd

def clean_and_analyze(df: pd.DataFrame) -> dict:
    """
    数据清洗与分析（学习：数据处理管道）

    知识点：
    - pipe()：自定义函数链
    - query()：字符串表达式筛选
    - assign()：动态添加列
    - 字典解包：返回多个结果

    练习：添加缺失值处理逻辑
    """

    # 检查DataFrame是否为空（学习：early return模式）
    if df.empty:
        return {"error": "数据为空"}

    # 重要：先转换类型，再清洗
    df = df.copy()
    df['销售额'] = pd.to_numeric(df['销售额'], errors='coerce')

    # 使用管道操作（学习：函数式编程）
    cleaned_df = (df
    .dropna(subset = ['销售额'])  # 删除销售额为空的行
    .query("销售额 > 0")  # 筛选销售额大于0
    .assign(
        销售额万 = lambda x: x['销售额'] / 10000,  # 添加新列
        是否高业绩 = lambda x: x['销售额'] > x['销售额'].mean()
    )
    )

    # 分组统计（学习：groupby聚合）
    summary = (cleaned_df
               .groupby('部门')
               .agg({
        '销售额': ['sum', 'mean', 'count'],
        '是否高业绩': 'sum'
        })
        .round(2)
    )

    # 练习：将summary的列名改为中文（使用set_axis方法）

    return {
        "cleaned_data": cleaned_df,
        "summary": summary,
        "total_records": len(cleaned_df)
    }


# 高级筛选示例（学习：布尔索引）
def advanced_filter(df: pd.DataFrame,
                    min_sales: float = 10000,
                    departments: list = None) -> pd.DataFrame:
    """
    高级筛选功能（学习：参数默认值和类型）

    知识点：
    - isin()：成员关系判断
    - &（按位与）和 |（按位或）
    - 括号的重要性：逻辑运算优先级

    练习：添加日期范围筛选
    """

    # 基础条件
    mask = df['销售额'] >= min_sales

    # 部门筛选（学习：None检查和列表操作）
    if departments is not None:
        mask = mask & df['部门'].isin(departments)

    # 应用筛选（学习：掩码Mask）
    filtered_df = df[mask].copy()  # 重要：使用copy避免SettingWithCopyWarning

    return filtered_df


# 学习检查点
if __name__ == "__main__":
    # # 创建测试数据（学习：生成随机数据）
    import numpy as np

    np.random.seed(42)  # 设置随机种子保证可重复性

    data = {
        '部门': np.random.choice(['销售部', '市场部', '技术部'], 100),
        '销售额': np.random.randint(5000, 50000, 100),
        '日期': pd.date_range('2025-01-01', periods = 100)
    }
    df = pd.DataFrame(data)

    # 调用函数
    result = clean_and_analyze(df)

    # raw_df = pd.DataFrame({
    #     '商品名称': ['iPhone', '华为', '小米'],
    #     '销售额': ['19999', '99999', '8999'],  # 有脏数据
    #     '部门': ['手机部', '手机部', '家电部']
    # })
    #
    # # 用我们的函数清洗
    # result = clean_and_analyze(raw_df)

    print(f"处理完成，共 {result['total_records']} 条有效记录")
    print("\n部门汇总:")
    print(result['summary'])