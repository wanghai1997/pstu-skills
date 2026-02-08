# -*- coding: utf-8 -*-
"""
报告生成模块
生成文本报告和Excel报告
"""

from datetime import datetime

import pandas as pd

from .config import CASH_FLOW_PORTRAITS, REPORT_CONFIG


def generate_text_report(results, output_file=None):
    """
    生成文本格式报告

    Args:
        results: 筛选结果列表或单个结果字典
        output_file: 输出文件路径，None则直接打印

    Returns:
        str: 报告文本内容
    """
    if isinstance(results, dict):
        results = [results]

    lines = []
    lines.append("=" * 80)
    lines.append("财报筛选报告")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)

    # 汇总统计
    total = len(results)
    passed = len([r for r in results if r.get('status') == '通过'])
    warning = len([r for r in results if r.get('status') == '预警'])
    excluded = len([r for r in results if r.get('status') == '排除'])

    lines.append(f"\n汇总统计:")
    lines.append(f"  总计分析: {total} 只股票")
    lines.append(f"  通过筛选: {passed} 只 ({passed/total*100:.1f}%)")
    lines.append(f"  需要预警: {warning} 只 ({warning/total*100:.1f}%)")
    lines.append(f"  建议排除: {excluded} 只 ({excluded/total*100:.1f}%)")

    # 详细结果
    lines.append("\n" + "=" * 80)
    lines.append("详细分析结果")
    lines.append("=" * 80)

    for i, result in enumerate(results, 1):
        lines.append(f"\n【{i}】{result.get('name', 'Unknown')} ({result.get('symbol', 'N/A')})")
        lines.append("-" * 80)
        lines.append(f"状态: {result.get('status', '未知')}")
        lines.append(f"综合得分: {result.get('score', 0)}/100")

        # 财务指标
        indicators = result.get('indicators', {})
        if indicators:
            lines.append("\n关键财务指标:")
            for name, value in indicators.items():
                if value is not None:
                    if name == 'cash_flow_portrait':
                        portrait_info = CASH_FLOW_PORTRAITS.get(value, {})
                        portrait_name = portrait_info.get('name', '未知')
                        lines.append(f"  {name}: {value} ({portrait_name})")
                    elif isinstance(value, float) and value != float('inf'):
                        if name in ['roe', 'gross_margin', 'net_margin', 'receivables_ratio',
                                   'debt_ratio', 'expense_ratio']:
                            lines.append(f"  {name}: {value*100:.2f}%")
                        else:
                            lines.append(f"  {name}: {value:.4f}")
                    else:
                        lines.append(f"  {name}: {value}")

        # 检查结果
        checks = result.get('checks', {})
        if checks:
            lines.append("\n筛选检查:")
            for check_name, check in checks.items():
                status = "[OK]" if check.get('passed') else "[X]"
                desc = check.get('description', '')
                lines.append(f"  {status} {check_name}: {desc}")

        # 排除原因
        exclusions = result.get('exclusions', [])
        if exclusions:
            lines.append("\n排除原因:")
            for exclusion in exclusions:
                lines.append(f"  [X] {exclusion}")

        # 风险提示
        warnings = result.get('warnings', [])
        if warnings:
            lines.append("\n风险提示:")
            for warning in warnings:
                lines.append(f"  [!] {warning}")

    lines.append("\n" + "=" * 80)
    lines.append("报告生成完成")
    lines.append("=" * 80)

    report_text = "\n".join(lines)

    # 输出到文件或打印
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"文本报告已保存到: {output_file}")
    else:
        print(report_text)

    return report_text


def generate_excel_report(results, filename=None):
    """
    生成Excel格式报告

    Args:
        results: 筛选结果列表
        filename: 输出文件名，默认使用配置中的文件名

    Returns:
        str: 生成的文件名
    """
    if isinstance(results, dict):
        results = [results]

    if filename is None:
        filename = REPORT_CONFIG.get('excel_filename', 'financial_screening_report.xlsx')

    # 准备数据
    summary_data = []
    detail_data = []

    for result in results:
        symbol = result.get('symbol', 'N/A')
        name = result.get('name', 'Unknown')
        status = result.get('status', '未知')
        score = result.get('score', 0)

        # 汇总数据
        summary_data.append({
            '股票代码': symbol,
            '股票名称': name,
            '筛选状态': status,
            '综合得分': score,
        })

        # 详细数据
        indicators = result.get('indicators', {})
        detail_row = {
            '股票代码': symbol,
            '股票名称': name,
            '筛选状态': status,
            '综合得分': score,
        }

        # 添加指标数据
        for name_key, value in indicators.items():
            if value is not None:
                if isinstance(value, float) and value != float('inf'):
                    # 百分比格式
                    if name_key in ['roe', 'gross_margin', 'net_margin', 'receivables_ratio',
                                   'debt_ratio', 'cash_flow_quality', 'expense_ratio']:
                        detail_row[name_key] = f"{value*100:.2f}%"
                    else:
                        detail_row[name_key] = f"{value:.4f}"
                else:
                    detail_row[name_key] = value

        detail_data.append(detail_row)

    # 创建Excel文件
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet 1: 汇总表
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='筛选汇总', index=False)

        # Sheet 2: 详细指标
        if detail_data:
            df_detail = pd.DataFrame(detail_data)
            df_detail.to_excel(writer, sheet_name='详细指标', index=False)

        # Sheet 3: 各股票检查明细
        checks_data = []
        for result in results:
            symbol = result.get('symbol', 'N/A')
            name = result.get('name', 'Unknown')
            checks = result.get('checks', {})

            for check_name, check in checks.items():
                checks_data.append({
                    '股票代码': symbol,
                    '股票名称': name,
                    '检查项': check_name,
                    '是否通过': '是' if check.get('passed') else '否',
                    '实际值': check.get('value'),
                    '阈值': check.get('threshold'),
                    '说明': check.get('description', ''),
                })

        if checks_data:
            df_checks = pd.DataFrame(checks_data)
            df_checks.to_excel(writer, sheet_name='检查明细', index=False)

        # Sheet 4: 风险提示
        warnings_data = []
        for result in results:
            symbol = result.get('symbol', 'N/A')
            name = result.get('name', 'Unknown')

            # 排除原因
            for exclusion in result.get('exclusions', []):
                warnings_data.append({
                    '股票代码': symbol,
                    '股票名称': name,
                    '类型': '排除',
                    '内容': exclusion,
                })

            # 风险提示
            for warning in result.get('warnings', []):
                warnings_data.append({
                    '股票代码': symbol,
                    '股票名称': name,
                    '类型': '预警',
                    '内容': warning,
                })

        if warnings_data:
            df_warnings = pd.DataFrame(warnings_data)
            df_warnings.to_excel(writer, sheet_name='风险提示', index=False)

    print(f"Excel报告已生成: {filename}")
    return filename


def generate_summary(results):
    """
    生成文字汇总统计

    Args:
        results: 筛选结果列表

    Returns:
        str: 汇总文字
    """
    if isinstance(results, dict):
        results = [results]

    total = len(results)
    passed = [r for r in results if r.get('status') == '通过']
    warning = [r for r in results if r.get('status') == '预警']
    excluded = [r for r in results if r.get('status') == '排除']

    lines = []
    lines.append("=" * 60)
    lines.append("财报筛选汇总")
    lines.append("=" * 60)
    lines.append(f"\n总计分析: {total} 只股票")
    lines.append(f"通过筛选: {len(passed)} 只 ({len(passed)/total*100:.1f}%)")
    lines.append(f"需要预警: {len(warning)} 只 ({len(warning)/total*100:.1f}%)")
    lines.append(f"建议排除: {len(excluded)} 只 ({len(excluded)/total*100:.1f}%)")

    if passed:
        lines.append("\n通过筛选的股票:")
        for r in sorted(passed, key=lambda x: x.get('score', 0), reverse=True):
            lines.append(f"  [OK] {r.get('name')} ({r.get('symbol')}) - 得分: {r.get('score')}")

    if warning:
        lines.append("\n需要预警的股票:")
        for r in warning:
            lines.append(f"  [!] {r.get('name')} ({r.get('symbol')}) - 得分: {r.get('score')}")
            for w in r.get('warnings', [])[:2]:  # 只显示前2个警告
                lines.append(f"      - {w}")

    if excluded:
        lines.append("\n建议排除的股票:")
        for r in excluded:
            lines.append(f"  [X] {r.get('name')} ({r.get('symbol')}) - 得分: {r.get('score')}")
            for e in r.get('exclusions', [])[:2]:  # 只显示前2个排除原因
                lines.append(f"      - {e}")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)
