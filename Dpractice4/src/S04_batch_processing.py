# src/S04_batch_processing.py
"""
学习目标：
1. os模块文件遍历
2. glob模式匹配
3. 函数组合和高阶函数
4. 日志记录（logging模块）
"""

import os
import glob
import pandas as pd
from datetime import datetime
import logging

# 配置日志（学习：日志级别和格式）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"logs/batch_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)


def process_single_file(file_path: str, output_dir: str) -> dict:
    """
    处理单个Excel文件（学习：单一职责原则）

    知识点：
    - 函数只做一件事
    - 返回字典包含处理结果
    - 异常捕获和日志记录

    练习：添加处理时间统计
    """
    try:
        logging.info(f"开始处理: {os.path.basename(file_path)}")

        # 读取数据
        df = pd.read_excel(file_path)

        # 数据处理（调用之前模块的函数）
        from S02_data_processing import clean_and_analyze
        result = clean_and_analyze(df)

        if "error" in result:
            logging.error(f"处理失败: {result['error']}")
            return {"status": "failed", "file": file_path}

        # 生成输出文件名（学习：路径拼接）
        output_path = os.path.join(
            output_dir,
            f"processed_{os.path.basename(file_path)}"
        )

        # 保存结果
        result['cleaned_data'].to_excel(output_path, index=False)

        logging.info(f"处理完成: {output_path}")
        return {"status": "success", "file": file_path, "records": result['total_records']}

    except Exception as e:
        logging.error(f"处理异常: {file_path} - {e}")
        return {"status": "error", "file": file_path, "message": str(e)}


def batch_process(folder_path: str, pattern: str = "*.xlsx"):
    """
    批量处理文件夹中的Excel文件（学习：迭代器和生成器）

    知识点：
    - glob.glob()：文件模式匹配
    - 列表推导式：收集处理结果
    - 生成器表达式（进阶）

    练习：改为使用生成器yield，处理大文件夹
    """

    # 检查文件夹是否存在
    if not os.path.isdir(folder_path):
        logging.error(f"文件夹不存在: {folder_path}")
        return []

    # 获取所有匹配的文件（学习：通配符）
    file_list = glob.glob(os.path.join(folder_path, pattern))
    logging.info(f"发现 {len(file_list)} 个待处理文件")

    # 创建输出目录（学习：exist_ok参数）
    output_dir = os.path.join(folder_path, "output")
    os.makedirs(output_dir, exist_ok = True)

    # 处理所有文件（学习：列表推导式）
    results = [process_single_file(f, output_dir) for f in file_list]

    # 统计结果（学习：列表推导式过滤）
    success_count = len([r for r in results if r['status'] == 'success'])
    logging.info(f"批量处理完成，成功: {success_count}/{len(results)}")

    return results


# 学习检查点
if __name__ == "__main__":
    # 创建测试文件
    import numpy as np

    for i in range(3):
        df = pd.DataFrame({
            '部门': np.random.choice(['A', 'B'], 10),
            '销售额': np.random.randint(1000, 10000, 10)
        })
        df.to_excel(f"D:\Automation_Test_Engineer\python_learning\Dpractice4\data/raw/test_{i}.xlsx", index = False)

    # 批量处理
    batch_process("D:\Automation_Test_Engineer\python_learning\Dpractice4\data/raw")