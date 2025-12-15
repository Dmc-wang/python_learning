# src/05_class_version.py
"""
学习目标：
1. 类的定义和实例化
2. 封装、继承、多态（基础）
3. 魔术方法（__init__, __str__）
4. 静态方法和类方法
"""

import pandas as pd
from pathlib import Path
import logging
from typing import Optional, List, Dict


class ExcelProcessor:
    """
    Excel处理器类（学习：面向对象封装）

    知识点：
    - 类属性 vs 实例属性
    - 类型注解：Optional, List, Dict
    - 私有方法（_method）
    - 属性装饰器（@property）

    练习：添加缓存机制，避免重复读取
    """

    # 类属性（学习：共享数据）
    supported_formats = ['.xlsx', '.xls', '.xlsm']

    def __init__(self, file_path: str, logger: Optional[logging.Logger] = None):
        """
        初始化处理器（学习：构造函数）

        知识点：
        - __init__魔术方法
        - 默认参数和Optional类型
        - 实例属性赋值
        """
        self.file_path = Path(file_path)
        self._data: Optional[pd.DataFrame] = None  # 私有属性
        self.logger = logger or logging.getLogger(__name__)

        # 验证文件格式（学习：断言和类属性）
        assert self.file_path.suffix in self.supported_formats, \
            f"不支持的文件格式: {self.file_path.suffix}"

    def load(self, sheet_name: int = 0) -> 'ExcelProcessor':
        """
        加载数据（学习：链式调用）

        知识点：
        - 返回self实现链式调用
        - 异常捕获和日志
        - pd.read_excel的参数

        练习：添加sheet_name的自动检测
        """
        try:
            self.logger.info(f"加载文件: {self.file_path.name}")
            self._data = pd.read_excel(self.file_path, sheet_name=sheet_name)
            return self  # 返回self支持链式调用

        except Exception as e:
            self.logger.error(f"加载失败: {e}")
            raise  # 重新抛出异常

    @property
    def data(self) -> pd.DataFrame:
        """
        数据属性（学习：属性装饰器）

        知识点：
        - @property将方法变为属性
        - 数据验证

        练习：添加只读保护
        """
        if self._data is None:
            raise ValueError("数据未加载，请先调用load()方法")
        return self._data

    @property
    def shape(self) -> tuple:
        """返回数据形状（学习：计算属性）"""
        if self._data is None:
            return (0, 0)
        return self.data.shape

    def filter_data(self, condition: str) -> pd.DataFrame:
        """
        筛选数据（学习：方法封装）

        知识点：
        - query()方法的应用
        - 返回新DataFrame（不修改原数据）

        练习：添加多种筛选模式
        """
        return self.data.query(condition).copy()

    def save(self, output_path: str, **kwargs) -> bool:
        """
        保存数据（学习：kwargs参数）

        知识点：
        - **kwargs接收额外参数
        - to_excel的参数传递
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            self.data.to_excel(output_path, index=False, **kwargs)
            self.logger.info(f"保存成功: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"保存失败: {e}")
            return False

    def __str__(self) -> str:
        """字符串表示（学习：__str__魔术方法）"""
        return f"ExcelProcessor({self.file_path.name}, shape={self.shape})"

    def __len__(self) -> int:
        """数据长度（学习：__len__魔术方法）"""
        return len(self.data) if self._data is not None else 0


# 批量处理器（学习：继承）
class BatchExcelProcessor:
    """
    批量处理器（学习：组合而非继承）

    知识点：
    - 组合模式：包含ExcelProcessor实例
    - 静态方法：不需要实例的功能
    - 类方法：替代构造函数
    """

    def __init__(self, folder_path: str):
        self.folder = Path(folder_path)
        self.processors: List[ExcelProcessor] = []

    @staticmethod
    def find_files(folder: Path, pattern: str = "*.xlsx") -> List[Path]:
        """静态方法查找文件（学习：无需self）"""
        return list(folder.glob(pattern))

    def load_all(self):
        """加载所有文件（学习：列表推导式）"""
        files = self.find_files(self.folder)
        self.processors = [ExcelProcessor(f) for f in files]
        return self

    def process_all(self, func) -> List[Dict]:
        """
        批量处理（学习：函数作为参数）

        知识点：
        - 高阶函数：func参数是可调用对象
        - map()和列表推导式
        """
        return [func(p) for p in self.processors]


# 学习检查点
if __name__ == "__main__":
    # 创建测试文件
    df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    df.to_excel("D:\Automation_Test_Engineer\python_learning\Dpractice4\data/raw/class_test.xlsx", index = False)

    # 使用类
    processor = ExcelProcessor("D:\Automation_Test_Engineer\python_learning\Dpractice4\data/raw/class_test.xlsx")
    processor.load()

    print(processor)  # 调用__str__
    print(f"数据长度: {len(processor)}")  # 调用__len__

    filtered = processor.filter_data("A > 1")
    print(f"\n筛选后:\n{filtered}")