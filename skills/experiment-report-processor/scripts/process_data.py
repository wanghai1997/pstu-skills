#!/usr/bin/env python3
"""
实验数据处理脚本
处理实验数据文件并返回统计结果
"""

import sys
import pandas as pd
import numpy as np
from typing import Dict, Any


def process_experiment_file(file_path: str) -> Dict[str, Any]:
    """
    处理实验数据文件

    Args:
        file_path: 数据文件路径 (.csv, .xlsx, .xls, .json)

    Returns:
        包含处理结果的字典
    """
    print(f"正在读取文件: {file_path}")

    # 根据文件扩展名选择读取方法
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path)
    elif file_path.endswith('.json'):
        df = pd.read_json(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {file_path}")

    print(f"成功读取 {len(df)} 行 {len(df.columns)} 列的数据")

    # 数据清洗
    print("正在进行数据清洗...")
    df_clean = df.dropna()  # 删除缺失值
    removed_rows = len(df) - len(df_clean)

    # 计算统计数据
    print("正在计算统计数据...")
    results = {
        'raw_data': df,
        'cleaned_data': df_clean,
        'sample_count': len(df_clean),
        'columns': list(df_clean.columns),
        'dtypes': {col: str(dtype) for col, dtype in df_clean.dtypes.items()},
        'missing_values': df.isnull().sum().to_dict(),
    }

    # 对每个数值列计算统计量
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        results['statistics'] = {}
        for col in numeric_cols:
            results['statistics'][col] = {
                'mean': float(df_clean[col].mean()),
                'std': float(df_clean[col].std()),
                'min': float(df_clean[col].min()),
                'max': float(df_clean[col].max()),
                'median': float(df_clean[col].median()),
            }

    results['data_quality'] = {
        'total_rows': len(df),
        'valid_rows': len(df_clean),
        'removed_rows': removed_rows,
        'completion_rate': len(df_clean) / len(df) * 100
    }

    return results


def save_processed_data(results: Dict[str, Any], output_path: str):
    """保存处理后的数据"""
    df_clean = results['cleaned_data']
    if output_path.endswith('.csv'):
        df_clean.to_csv(output_path, index=False)
    elif output_path.endswith('.xlsx'):
        df_clean.to_excel(output_path, index=False)
    else:
        raise ValueError("不支持的输出格式")

    print(f"数据已保存到: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python process_data.py <输入文件> [输出文件]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        result = process_experiment_file(input_file)

        print("\n=== 数据处理完成 ===")
        print(f"样本数量: {result['sample_count']}")
        print(f"数据列: {', '.join(result['columns'])}")

        if 'statistics' in result:
            print("\n=== 数值统计 ===")
            for col, stats in result['statistics'].items():
                print(f"{col}: 均值={stats['mean']:.2f}, 标准差={stats['std']:.2f}")

        if output_file:
            save_processed_data(result, output_file)

    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)
