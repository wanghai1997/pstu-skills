# -*- coding: utf-8 -*-
"""
财报筛选器测试脚本

这个脚本用于验证财报筛选器的功能是否正常工作
"""

import sys

# 添加当前目录到路径，以便导入financial_screener
sys.path.insert(0, 'd:\\fuyong\\stu_test\\pstu')

from financial_screener import FinancialScreener
from financial_screener.report_generator import (
    generate_text_report,
    generate_excel_report,
    generate_summary
)


def test_single_stock():
    """
    测试单只股票分析
    使用贵州茅台(600519)作为测试案例
    """
    print("\n" + "="*60)
    print("测试1: 单只股票分析")
    print("="*60)

    screener = FinancialScreener(use_cache=True)

    # 分析贵州茅台
    result = screener.screen_single("600519")

    print("\n测试完成！")
    print(f"股票: {result['name']} ({result['symbol']})")
    print(f"状态: {result['status']}")
    print(f"得分: {result['score']}/100")

    return result


def test_batch_screening():
    """
    测试批量筛选
    选取几只不同行业的股票进行对比
    """
    print("\n" + "="*60)
    print("测试2: 批量筛选")
    print("="*60)

    screener = FinancialScreener(use_cache=True)

    # 选取几只股票：
    # 600519 - 贵州茅台（白酒）
    # 000001 - 平安银行（银行）
    # 000858 - 五粮液（白酒）
    # 002415 - 海康威视（科技）
    symbols = ["600519", "000001", "000858", "002415"]

    results = screener.screen_batch(symbols)

    return results


def test_report_generation(results):
    """
    测试报告生成功能
    """
    print("\n" + "="*60)
    print("测试3: 报告生成")
    print("="*60)

    # 生成文本汇总
    print("\n生成文字汇总...")
    summary = generate_summary(results)
    print(summary)

    # 生成Excel报告
    print("\n生成Excel报告...")
    excel_file = generate_excel_report(results, "test_report.xlsx")
    print(f"Excel报告已保存: {excel_file}")

    return summary


def test_cache_functionality():
    """
    测试缓存功能
    """
    print("\n" + "="*60)
    print("测试4: 缓存功能")
    print("="*60)

    screener = FinancialScreener(use_cache=True)

    # 查看缓存信息
    cache_info = screener.get_cache_info()
    print("\n当前缓存信息:")
    for key, value in cache_info.items():
        print(f"  {key}: {value}")

    return cache_info


def main():
    """
    主测试函数
    """
    print("="*60)
    print("财报筛选器功能测试")
    print("="*60)
    print("\n本测试将验证以下功能:")
    print("1. 单只股票深度分析")
    print("2. 多只股票批量筛选")
    print("3. 报告生成（文本 + Excel）")
    print("4. 缓存功能")
    print("\n注意: 首次运行需要从AKShare下载数据，可能需要一些时间...")
    print("="*60)

    try:
        # 测试1: 单只股票
        single_result = test_single_stock()

        # 测试2: 批量筛选
        batch_results = test_batch_screening()

        # 测试3: 报告生成
        test_report_generation(batch_results)

        # 测试4: 缓存功能
        test_cache_functionality()

        # 最终总结
        print("\n" + "="*60)
        print("所有测试完成!")
        print("="*60)
        print("\n生成的文件:")
        print("  - test_report.xlsx (Excel筛选报告)")
        print("\n缓存的数据保存在 data/cache/ 目录")
        print("\n你可以修改本脚本中的 symbols 列表，测试更多股票!")

    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
