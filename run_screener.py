# -*- coding: utf-8 -*-
"""
财报筛选器运行脚本

基于《手把手教你读财报》核心规则的自动化财报筛选系统

使用方法:
    python run_screener.py [选项] [股票代码]

示例:
    python run_screener.py 600519          # 分析单只股票
    python run_screener.py --hs300         # 分析全部沪深300成分股
    python run_screener.py --all           # 分析数据库中所有股票
    python run_screener.py                 # 分析默认5只股票
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from financial_screener import FinancialScreener
from data_manager import DatabaseManager


def main():
    # 解析命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1]

        if arg == '--hs300':
            # 分析全部沪深300
            run_hs300_screening()
        elif arg == '--all':
            # 分析数据库中所有股票
            run_all_screening()
        elif arg.startswith('--'):
            print(f"未知选项: {arg}")
            print("可用选项: --hs300, --all")
        else:
            # 单只股票分析
            symbol = arg
            print(f"分析单只股票: {symbol}")
            screener = FinancialScreener()
            result = screener.screen_single(symbol)
    else:
        # 批量分析默认列表
        run_default_screening()


def run_default_screening():
    """运行默认5只股票分析"""
    print("=" * 70)
    print("财报筛选器 - 批量分析 (默认5只)")
    print("=" * 70)

    test_symbols = [
        "600519",  # 贵州茅台
        "000858",  # 五粮液
        "300750",  # 宁德时代
        "000001",  # 平安银行
        "002415",  # 海康威视
    ]

    print(f"\n分析股票列表: {', '.join(test_symbols)}")
    print("\n开始分析...")
    print("=" * 70)

    screener = FinancialScreener()
    results = screener.screen_batch(test_symbols)

    generate_report(results, "筛选结果_默认5只.xlsx")


def run_hs300_screening():
    """分析全部沪深300成分股"""
    print("=" * 70)
    print("财报筛选器 - 沪深300全成分股分析")
    print("=" * 70)

    # 从数据库获取沪深300股票列表
    db = DatabaseManager()
    symbols = db.get_symbols_with_data()

    if len(symbols) > 300:
        # 只取前300只（假设是沪深300）
        symbols = symbols[:300]

    print(f"\n准备分析 {len(symbols)} 只沪深300成分股")
    print("预计耗时: 5-10 分钟")
    print("=" * 70)

    try:
        screener = FinancialScreener()
        results = screener.screen_batch(symbols)
        generate_report(results, "筛选结果_沪深300.xlsx")
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消分析")


def run_all_screening():
    """分析数据库中所有有财务数据的股票"""
    print("=" * 70)
    print("财报筛选器 - 全市场分析")
    print("=" * 70)

    db = DatabaseManager()
    # 从financial_abstract表获取有财务数据的股票（而非daily_prices）
    symbols = db.get_symbols_with_financial_data()

    print(f"\n数据库中共有 {len(symbols)} 只股票")
    print("预计耗时: 视股票数量而定")
    print("=" * 70)

    try:
        screener = FinancialScreener()
        results = screener.screen_batch(symbols)
        generate_report(results, "筛选结果_全市场.xlsx")
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消分析")


def generate_report(results, filename):
    """生成Excel报告"""
    try:
        from financial_screener.report_generator import generate_excel_report
        generate_excel_report(results, filename)
        print(f"\n[OK] Excel报告已生成: {filename}")
    except Exception as e:
        print(f"\n[WARN] Excel报告生成失败: {e}")


if __name__ == "__main__":
    main()
