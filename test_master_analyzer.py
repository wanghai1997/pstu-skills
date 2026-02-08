# -*- coding: utf-8 -*-
"""
投资大师分析系统测试脚本

测试多周期分析和置信度计算功能
"""

import sys

sys.path.insert(0, 'd:\\fuyong\\stu_test\\pstu')

from investment_master import MasterAnalyzer


def test_single_stock():
    """
    测试单只股票分析
    """
    print("="*60)
    print("投资大师分析系统 - 单只股票测试")
    print("="*60)

    analyzer = MasterAnalyzer()

    # 测试茅台
    result = analyzer.analyze("600519")

    print("\n" + "="*60)
    print("分析结果摘要")
    print("="*60)
    print(f"\n股票: {result['name']} ({result['symbol']})")
    print(f"置信度: {result['confidence']:.1f}%")
    print(f"操作建议: {result['action']}")
    print(f"仓位建议: {result['position']}")
    print(f"止损: {result['stop_loss']}")
    print(f"止盈: {result['take_profit']}")

    return result


def test_batch_analysis():
    """
    测试批量分析
    使用之前财报筛选器通过的6只股票
    """
    print("\n" + "="*60)
    print("投资大师分析系统 - 批量测试")
    print("="*60)

    # 财报筛选器通过的股票
    passed_stocks = ["600519", "600809", "000333", "300760", "000858", "300750"]

    analyzer = MasterAnalyzer()
    results = analyzer.batch_analyze(passed_stocks)

    return results


def main():
    """
    主测试函数
    """
    print("="*60)
    print("投资大师分析系统测试")
    print("="*60)
    print("\n本系统特点:")
    print("- 多周期分析: 周线/日线/60分钟/15分钟")
    print("- 置信度计算: 5维度加权评分")
    print("- 操作策略: 根据置信度自动生成")
    print("\n注意: 需要下载K线数据，可能需要几分钟...")
    print("="*60)

    try:
        # 测试1: 单只股票
        print("\n【测试1】单只股票深度分析")
        single_result = test_single_stock()

        # 询问是否继续批量测试
        print("\n" + "="*60)
        confirm = input("\n是否继续批量测试(6只股票)? (y/n): ")

        if confirm.lower() == 'y':
            # 测试2: 批量分析
            print("\n【测试2】批量分析")
            batch_results = test_batch_analysis()

        print("\n" + "="*60)
        print("测试完成!")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    except Exception as e:
        print(f"\n测试出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
