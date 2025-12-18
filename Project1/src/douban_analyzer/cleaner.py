"""
豆瓣电影数据清洗模块
支持类型转换、缺失值处理、异常值检测、数据质量报告
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

import numpy as np
import pandas as pd

# from .fetcher import Movie


@dataclass
class CleanerConfig:
    """清洗配置类"""
    # 输入输出路径
    input_dir: Path = Path("data/raw")
    output_dir: Path = Path("data/processed")
    
    # 数据类型映射
    dtype_mapping: Dict[str, str] = field(default_factory=lambda: {
        'rank': 'Int16',           # 排名（可为空）
        'title': 'string',         # 标题（不可为空）
        'rating': 'float32',       # 评分
        'rating_count': 'Int64',   # 评价人数
        'quote': 'string',         # 简介（可为空）
        'year': 'Int16',           # 年份
        'director': 'string',      # 导演
        'actors': 'string',        # 演员（可为空）
        'genres': 'string',        # 类型
        'duration': 'string',      # 时长（可为空）
    })
    
    # 清洗规则
    min_rating: float = 8.0      # 最低评分阈值
    min_rating_count: int = 5000  # 最低评价人数
    drop_duplicates_by: List[str] = field(default_factory=lambda: ['title', 'year'])
    
    # 缺失值处理策略
    fill_na_values: Dict[str, Any] = field(default_factory=lambda: {
        'quote': '暂无简介',
        'actors': '暂无演员信息',
        'duration': '未知',
    })


class DataCleaner:
    """数据清洗器主类"""
    
    def __init__(self, config: Optional[CleanerConfig] = None):
        self.config = config or CleanerConfig()
        self.logger = self._setup_logger()
        self.raw_df: Optional[pd.DataFrame] = None
        self.cleaned_df: Optional[pd.DataFrame] = None
        self.report: Dict[str, Any] = {}
    
    def _setup_logger(self) -> logging.Logger:
        """配置日志"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def load_data(self, filename: Optional[str] = None) -> pd.DataFrame:
        """
        加载原始数据
        
        Args:
            filename: CSV文件名，None则自动查找最新文件
        
        Returns:
            原始DataFrame
        """
        if filename:
            input_path = self.config.input_dir / filename
        else:
            # 自动查找最新的CSV文件
            csv_files = list(self.config.input_dir.glob("movies_top250_*.csv"))
            if not csv_files:
                raise FileNotFoundError(f"在 {self.config.input_dir} 中未找到数据文件")
            input_path = max(csv_files, key=lambda p: p.stat().st_mtime)
        
        self.logger.info(f"正在加载数据: {input_path}")
        
        # 读取CSV（注意编码和缺失值表示）
        df = pd.read_csv(
            input_path,
            dtype=self.config.dtype_mapping,
            na_values=['', 'NULL', 'null', 'N/A', 'NaN']
        )
        
        self.logger.info(f"加载完成！共{len(df)}行，{len(df.columns)}列")
        self.raw_df = df
        return df
    
    def validate_schema(self, df: pd.DataFrame) -> bool:
        """
        验证数据模式（Schema Validation）
        
        Returns:
            是否通过验证
        """
        self.logger.info("开始数据模式验证...")
        
        required_columns = list(self.config.dtype_mapping.keys())
        missing_cols = set(required_columns) - set(df.columns)
        
        if missing_cols:
            self.logger.error(f"缺失必需列: {missing_cols}")
            return False
        
        # 检查关键列的非空
        critical_columns = ['title', 'rating', 'rank']
        for col in critical_columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                self.logger.warning(f"关键列 '{col}' 有{null_count}个空值")
        
        self.logger.info("数据模式验证通过")
        return True
    
    def clean_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据类型转换和规范化
        """
        self.logger.info("开始类型转换...")
        
        # 转换为配置中指定的类型
        for col, dtype in self.config.dtype_mapping.items():
            if col in df.columns:
                try:
                    # 特殊处理：字符串类型
                    if dtype == 'string':
                        df[col] = df[col].astype('string')
                    else:
                        df[col] = df[col].astype(dtype)
                except Exception as e:
                    self.logger.warning(f"列 '{col}' 转换类型失败: {e}")
        
        # 特殊处理：评价人数中的缺失值
        if 'rating_count' in df.columns:
            df['rating_count'] = pd.to_numeric(
                df['rating_count'],
                errors='coerce'
            ).astype('Int64')
        
        self.logger.info("类型转换完成")
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        处理缺失值
        """
        self.logger.info("开始处理缺失值...")
        
        missing_report = {}
        
        for col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                missing_report[col] = null_count
                self.logger.info(f"列 '{col}' 有{null_count}个缺失值({null_count/len(df)*100:.1f}%)")
        
        # 根据配置填充缺失值
        for col, fill_value in self.config.fill_na_values.items():
            if col in df.columns:
                df[col] = df[col].fillna(fill_value)
                self.logger.info(f"列 '{col}' 已填充缺失值: {fill_value}")
        
        # 删除关键列仍有缺失的行
        critical_columns = ['title', 'rating', 'rank']
        df = df.dropna(subset=critical_columns)
        
        self.logger.info(f"缺失值处理完成，剩余{len(df)}行")
        self.report['missing_values'] = missing_report
        return df
    
    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        去重处理
        """
        self.logger.info("开始去重...")
        
        before_count = len(df)
        
        # 根据配置的列去重
        df = df.drop_duplicates(
            subset=self.config.drop_duplicates_by,
            keep='first'
        )
        
        after_count = len(df)
        removed = before_count - after_count
        
        self.logger.info(f"去重完成，删除{removed}条重复数据")
        self.report['duplicates_removed'] = removed
        
        return df
    
    def extract_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        特征工程：从现有数据提取新特征
        """
        self.logger.info("开始特征提取...")
        
        # 提取年份（如果尚未提取）
        if 'year' in df.columns:
            # 确保year是数值类型
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
            self.logger.info("年份列已转换为数值类型")
        
        # 创建评分等级
        def rating_grade(rating):
            if pd.isna(rating):
                return '未知'
            elif rating >= 9.5:
                return '神作'
            elif rating >= 9.0:
                return '经典'
            elif rating >= 8.5:
                return '佳作'
            elif rating >= 8.0:
                return '优秀'
            else:
                return '良好'
        
        df['rating_grade'] = df['rating'].apply(rating_grade)
        self.logger.info("新增列: rating_grade（评分等级）")
        
        # 计算评价人数的对数（用于后续分析）
        if 'rating_count' in df.columns:
            df['log_rating_count'] = np.log10(df['rating_count'].replace(0, 1))
            self.logger.info("新增列: log_rating_count（评价人数对数）")
        
        # 解析duration为分钟数
        def parse_duration(duration_str):
            if pd.isna(duration_str) or duration_str == '未知':
                return None
            try:
                # 格式: "142分钟" 或 "142分钟 / 导演剪辑版"
                import re
                match = re.search(r'(\d+)\s*分钟', str(duration_str))
                if match:
                    return int(match.group(1))
            except:
                pass
            return None
        
        df['duration_minutes'] = df['duration'].apply(parse_duration)
        df['duration_minutes'] = df['duration_minutes'].astype('Int16')
        self.logger.info("新增列: duration_minutes（时长分钟数）")
        
        return df
    
    def filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        数据过滤：删除不符合条件的数据
        """
        self.logger.info("开始数据过滤...")
        
        before_count = len(df)
        
        # 评分过滤
        if 'rating' in df.columns:
            df = df[df['rating'] >= self.config.min_rating]
            self.logger.info(f"应用评分阈值 ≥{self.config.min_rating}")
        
        # 评价人数过滤
        if 'rating_count' in df.columns:
            df = df[df['rating_count'] >= self.config.min_rating_count]
            self.logger.info(f"应用评价人数阈值 ≥{self.config.min_rating_count}")
        
        after_count = len(df)
        filtered = before_count - after_count
        
        self.logger.info(f"过滤完成，删除{filtered}条不符合条件的数据")
        self.report['filtered_out'] = filtered
        
        return df
    
    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        数据质量检查
        """
        self.logger.info("开始数据质量检查...")
        
        quality_report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'null_counts': df.isnull().sum().to_dict(),
            'duplicates': df.duplicated().sum(),
            'rating_stats': {
                'min': df['rating'].min(),
                'max': df['rating'].max(),
                'mean': df['rating'].mean(),
                'median': df['rating'].median(),
            } if 'rating' in df.columns else {},
            'year_range': {
                'min': df['year'].min(),
                'max': df['year'].max(),
            } if 'year' in df.columns else {},
        }
        
        # 检查异常值
        if 'rating' in df.columns:
            outliers = df[(df['rating'] < 8.0) | (df['rating'] > 10.0)]
            quality_report['rating_outliers'] = len(outliers)
        
        if 'year' in df.columns:
            year_outliers = df[(df['year'] < 1900) | (df['year'] > 2030)]
            quality_report['year_outliers'] = len(year_outliers)
        
        self.logger.info("数据质量检查完成")
        return quality_report
    
    def clean(self, input_file: Optional[str] = None) -> pd.DataFrame:
        """
        执行完整清洗流程
        
        Returns:
            清洗后的DataFrame
        """
        self.logger.info("=" * 50)
        self.logger.info("开始数据清洗流程...")
        
        # 1. 加载数据
        df = self.load_data(input_file)
        
        # 2. 验证模式
        if not self.validate_schema(df):
            raise ValueError("数据模式验证失败")
        
        # 3. 类型转换
        df = self.clean_types(df)
        
        # 4. 处理缺失值
        df = self.handle_missing_values(df)
        
        # 5. 去重
        df = self.remove_duplicates(df)
        
        # 6. 特征工程
        df = self.extract_features(df)
        
        # 7. 数据过滤
        df = self.filter_data(df)
        
        # 8. 质量检查
        self.report['quality'] = self.validate_data_quality(df)
        
        self.cleaned_df = df
        self.logger.info("数据清洗流程完成！")
        self.logger.info("=" * 50)
        
        return df
    
    def save_cleaned_data(self, df: Optional[pd.DataFrame] = None, 
                         output_format: str = 'csv') -> Path:
        """
        保存清洗后的数据
        
        Args:
            df: DataFrame，None则使用self.cleaned_df
            output_format: 输出格式 ('csv', 'json', 'excel')
        
        Returns:
            输出文件路径
        """
        if df is None:
            df = self.cleaned_df
        
        if df is None:
            raise ValueError("没有可保存的数据")
        
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format == 'csv':
            output_path = self.config.output_dir / f"cleaned_movies_{timestamp}.csv"
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
        elif output_format == 'json':
            output_path = self.config.output_dir / f"cleaned_movies_{timestamp}.json"
            df.to_json(output_path, orient='records', force_ascii=False, indent=2)
        elif output_format == 'excel':
            output_path = self.config.output_dir / f"cleaned_movies_{timestamp}.xlsx"
            df.to_excel(output_path, index=False, engine='openpyxl')
        else:
            raise ValueError(f"不支持的格式: {output_format}")
        
        self.logger.info(f"清洗数据已保存: {output_path}")
        return output_path
    
    def save_report(self, report: Optional[Dict[str, Any]] = None) -> Path:
        """
        保存清洗报告
        """
        if report is None:
            report = self.report
        
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.config.output_dir / f"cleaning_report_{timestamp}.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"清洗报告已保存: {report_path}")
        return report_path


# ==================== 命令行接口 ====================

def main():
    """主入口函数"""
    logging.basicConfig(level=logging.INFO)
    
    cleaner = DataCleaner()
    
    try:
        # 执行清洗
        cleaned_df = cleaner.clean()
        
        # 保存数据
        output_path = cleaner.save_cleaned_data(cleaned_df, output_format='csv')
        
        # 保存报告
        report_path = cleaner.save_report()
        
        print("\n" + "=" * 50)
        print("✅ 数据清洗完成！")
        print(f"清洗后数据: {len(cleaned_df)}行 × {len(cleaned_df.columns)}列")
        print(f"数据文件: {output_path}")
        print(f"报告文件: {report_path}")
        print("=" * 50)
        
        # 预览数据
        print("\n📊 预览前5行:")
        print(cleaned_df.head())
        
        # 显示质量报告摘要
        print("\n📈 质量报告摘要:")
        print(f"  - 删除重复数据: {cleaner.report.get('duplicates_removed', 0)}条")
        print(f"  - 过滤数据: {cleaner.report.get('filtered_out', 0)}条")
        
        quality = cleaner.report.get('quality', {})
        if 'rating_stats' in quality:
            stats = quality['rating_stats']
            print(f"  - 评分范围: {stats['min']:.1f} - {stats['max']:.1f}")
            print(f"  - 平均评分: {stats['mean']:.2f}")
        
    except Exception as e:
        print(f"❌ 清洗失败: {e}")
        raise


if __name__ == "__main__":
    main()