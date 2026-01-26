#!/usr/bin/env python3
"""
实验报告生成脚本
从处理过的数据生成格式化的报告
"""

import sys
from pathlib import Path
from jinja2 import Template
import pandas as pd


def create_experiment_report(data, template_path, output_path):
    """
    从实验数据生成报告

    Args:
        data: 处理过的实验数据
        template_path: 报告模板路径
        output_path: 输出报告路径
    """
    print(f"正在读取模板: {template_path}")

    # 读取模板
    template_content = Path(template_path).read_text(encoding='utf-8')
    template = Template(template_content)

    # 准备模板变量
    template_vars = {
        'title': '实验报告',
        'sample_count': data.get('sample_count', 0),
        'data_quality': data.get('data_quality', {}),
        'columns': data.get('columns', []),
        'statistics': data.get('statistics', {}),
    }

    # 渲染模板
    report_content = template.render(**template_vars)

    # 保存报告
    Path(output_path).write_text(report_content, encoding='utf-8')
    print(f"报告已生成: {output_path}")

    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python generate_report.py <数据文件> <模板> <输出文件>")
        sys.exit(1)

    data_file = sys.argv[1]
    template = sys.argv[2]
    output = sys.argv[3]

    try:
        # 读取数据
        import json
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        create_experiment_report(data, template, output)

    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)
