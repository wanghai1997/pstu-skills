# -*- coding: utf-8 -*-
"""
本地数据库测试脚本

测试从本地数据库读取数据进行分析
"""

import sys
import time

from data_manager import DataManager


def test_data_manager():
    """测试数据管理器"""
    print("="*70)
    print("测试1: 数据管理器")
    print("="*70)

    dm = DataManager()

    # 检查数据状态
    print("\n数据库状态:")
    stats = dm.get_stats()
    for table, count in stats.items():
        print(f"  {table:25s}: {count:8,} 条")

    # 获取有数据的股票列表
    symbols = dm.get_symbols()
    print(f"\n有数据的股票: {len(symbols)} 只")

    if not symbols:
        print("\n[错误] 本地数据库为空！")
        print("请先运行: python download_data.py")
        return None

    return symbols


def test_local_data_query(symbol="600519"):
    """测试本地数据查询"""
    print("\n" + "="*70)
    print("测试2: 本地数据查询")
    print("="*70)

    dm = DataManager()

    print(f"\n查询 {symbol} 的数据...")

    # 查询日线
    print("\n日线数据:")
    daily = dm.get_daily_prices(symbol, days=5)
    if daily is not None and not daily.empty:
        print(f"  ✓ 获取成功: {len(daily)} 条")
        print(f"  最新数据: {daily.index[-1].strftime('%Y-%m-%d')}, 收盘: {daily.iloc[-1]['close']}")
    else:
        print("  ✗ 无数据")

    # 查询周线
    print("\n周线数据:")
    weekly = dm.get_weekly_prices(symbol, weeks=5)
    if weekly is not None and not weekly.empty:
        print(f"  ✓ 获取成功: {len(weekly)} 条")
    else:
        print("  ✗ 无数据")

    # 查询60分钟
    print("\n60分钟数据:")
    min60 = dm.get_min60_prices(symbol, days=5)
    if min60 is not None and not min60.empty:
        print(f"  ✓ 获取成功: {len(min60)} 条")
    else:
        print("  ✗ 无数据")

    # 查询15分钟
    print("\n15分钟数据:")
    min15 = dm.get_min15_prices(symbol, days=3)
    if min15 is not None and not min15.empty:
        print(f"  ✓ 获取成功: {len(min15)} 条")
    else:
        print("  ✗ 无数据")

    # 查询财务数据
    print("\n财务数据:")
    financial = dm.get_financial_data(symbol)
    if financial:
        abstract = financial.get('abstract')
        if abstract is not None and not abstract.empty:
            print(f"  ✓ 获取成功: {len(abstract)} 期财报")
            # 显示最新一期关键指标
            latest = abstract.iloc[0]
            print(f"\n  最新一期 ({latest.get('报告期', 'N/A')}):")
            print(f"    ROE: {latest.get('净资产收益率', 'N/A')}")
            print(f"    毛利率: {latest.get('销售毛利率', 'N/A')}")
        else:
            print("  ✗ 无数据")


def test_financial_screener(symbol="600519"):
    """测试财报筛选器（本地模式）"""
    print("\n" + "="*70)
    print("测试3: 财报筛选器（本地数据库模式）")
    print("="*70)

    try:
        from financial_screener import FinancialScreener

        print(f"\n分析 {symbol}...")

        # 使用本地数据库模式
        screener = FinancialScreener(use_cache=True, use_local_db=True)
        result = screener.screen_single(symbol)

        print(f"\n结果:")
        print(f"  状态: {result.get('status', 'N/A')}")
        print(f"  得分: {result.get('score', 0)}/100")

        indicators = result.get('indicators', {})
        print(f"  ROE: {indicators.get('roe', 0)*100:.2f}%")
        print(f"  毛利率: {indicators.get('gross_margin', 0)*100:.2f}%")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


def test_master_analyzer(symbol="600519"):
    """测试投资大师系统（本地模式）"""
    print("\n" + "="*70)
    print("测试4: 投资大师系统（本地数据库模式）")
    print("="*70)

    try:
        from investment_master import MasterAnalyzer

        print(f"\n分析 {symbol}...")

        # 使用本地数据库（默认）
        analyzer = MasterAnalyzer()
        result = analyzer.analyze(symbol)

        print(f"\n结果:")
        print(f"  置信度: {result.get('confidence', 0):.1f}%")
        print(f"  操作建议: {result.get('action', 'N/A')}")
        print(f"  仓位建议: {result.get('position', 'N/A')}")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    print("="*70)
    print("本地数据库功能测试")
    print("="*70)
    print("\n本测试将验证：")
    print("  1. 数据管理器是否正常工作")
    print("  2. 本地数据查询是否正确")
    print("  3. 财报筛选器能否使用本地数据")
    print("  4. 投资大师系统能否使用本地数据")
    print("="*70)

    # 测试1：数据管理器
    symbols = test_data_manager()
    if not symbols:
        return

    # 使用第一只有数据的股票进行测试
    test_symbol = symbols[0]
    print(f"\n将使用 {test_symbol} 进行后续测试")

    # 测试2：本地数据查询
    test_local_data_query(test_symbol)

    # 测试3：财报筛选器
    confirm = input("\n是否测试财报筛选器? (y/n): ")
    if confirm.lower() == 'y':
        test_financial_screener(test_symbol)

    # 测试4：投资大师系统
    confirm = input("\n是否测试投资大师系统? (y/n): ")
    if confirm.lower() == 'y':
        test_master_analyzer(test_symbol)

    print("\n" + "="*70)
    print("测试完成！")
    print("="*70)


if __name__ == "__main__":
    main()
