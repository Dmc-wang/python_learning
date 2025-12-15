# src/S01_basic_io.py
"""
学习目标：
1. Python文件路径处理（raw字符串、Path对象）
2. try-except异常捕获
3. with上下文管理器
4. 函数定义和文档字符串
"""

import pandas as pd
from pathlib import Path


def read_excel_safely(file_path: str, sheet_name: int = 0) -> pd.DataFrame | None:
    """
    安全读取Excel文件（学习：异常处理+类型注解）

    知识点：
    - Union类型：pd.DataFrame | None 表示可能返回None
    - try-except：捕获特定异常类型
    - f-string：格式化字符串

    练习：修改代码，支持sheet_name为字符串的情况
    """
    try:
        # 使用Path处理跨平台路径问题
        path = Path(file_path)

        # 检查文件是否存在（学习：断言和条件判断）
        assert path.exists(), f"文件不存在: {path.absolute()}"

        # 读取数据（学习：函数参数默认值）
        df = pd.read_excel(path, sheet_name = sheet_name)
        print(f"✅ 成功读取 {path.name}，形状: {df.shape}")
        return df

    except FileNotFoundError as e:
        print(f"❌ 文件未找到错误: {e}")
        return None
    except ValueError as e:
        print(f"❌ Sheet名称错误: {e}")
        return None
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return None


def write_excel_with_backup(df: pd.DataFrame, output_path: str) -> bool:
    """
    写入Excel并创建备份（学习：文件备份、返回值）

    知识点：
    - bool返回值：表示操作成功/失败
    - Path.parent：获取父目录
    - 列表推导式：生成备份文件名

    练习：添加时间戳到备份文件名
    """
    try:
        from datetime import datetime

        path = Path(output_path)
        backup_dir = path.parent / "backup"
        backup_dir.mkdir(exist_ok = True)  # 创建备份目录

        # 如果文件存在，先备份（学习：文件重命名）
        if path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = backup_dir / f"{path.stem}_{timestamp}{path.suffix}"
            path.rename(backup_name)
            print(f"📁 原文件已备份为: {backup_name}")

        # 写入新数据（学习：index=False参数）
        df.to_excel(path, index = False, engine = 'openpyxl')
        print(f"✅ 文件已保存至: {path.absolute()}")
        return True

    except Exception as e:
        print(f"❌ 写入失败: {e}")
        return False


# 学习检查点
if __name__ == "__main__":
    # 测试数据（学习：字典创建DataFrame）
    test_data = {
        '姓名': ['张三', '李四', '王五'],
        '年龄': [25, 30, 28],
        '城市': ['北京', '上海', '深圳']
    }
    df = pd.DataFrame(test_data)

    # 调用函数
    write_excel_with_backup(df, r"D:\Automation_Test_Engineer\python_learning\Dpractice4\data\raw\output_test.xlsx")
    result_df = read_excel_safely(r"D:\Automation_Test_Engineer\python_learning\Dpractice4\data\raw\output_test.xlsx")

    # 练习：打印前3行数据（使用head()方法）
    if result_df is not None:
        print("\n预览数据:")
        print(result_df.head(3))