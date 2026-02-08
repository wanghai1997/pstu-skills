# -*- coding: utf-8 -*-
"""
简化测试 - 单只股票

测试整合选股系统的基本功能
"""

import sys
import time

sys.path.insert(0, 'd:\\fuyong\\stu_test\\pstu')

from investment_master import MasterAnalyzer
from financial_screener import FinancialScreener


def test_single():
    """测试单只股票"""
    print("="*70)
    print("整合选股系统 - 单只股票测试")
    print("="*70)
    print("\n股票: 贵州茅台 (600519)")
    print("\n说明:")
    print("  1. 先用投资大师系统分析技术面")
    print("  2. 再用财报筛选器确认基本面")
    print("  3. 双重确认后推荐")
    print("="*70)

    symbol = "600519"

    # 第一阶段：技术面分析
    print("\n【第一阶段】技术面分析...")
    print("-"*70)

    try:
        analyzer = MasterAnalyzer()
        tech_result = analyzer.analyze(symbol)

        confidence = tech_result.get('confidence', 0)
        action = tech_result.get('action', '未知')

        print(f"\n技术面结果:")
        print(f"  置信度: {confidence:.1f}%")
        print(f"  操作建议: {action}")

        # 检查是否通过技术面筛选
        if confidence < 65:
            print(f"\n[未通过] 技术面置信度 {confidence:.1f}% < 65%，不进入第二阶段")
            return

        print(f"\n[通过] 技术面优秀，进入第二阶段...")

    except Exception as e:
        print(f"技术面分析失败: {e}")
        import traceback
        traceback.print_exc()
        return

    time.sleep(2)

    # 第二阶段：基本面分析
    print("\n【第二阶段】基本面分析...")
    print("-"*70)

    try:
        screener = FinancialScreener()
        fund_result = screener.screen_single(symbol)

        status = fund_result.get('status', '未知')
        score = fund_result.get('score', 0)

        print(f"\n基本面结果:")
        print(f"  状态: {status}")
        print(f"  得分: {score}/100")

        # 整合结果
        print("\n" + "="*70)
        print("【最终结果】")
        print("="*70)

        if status == '通过':
            print(f"\n✓ 双重确认!")
            print(f"  股票: {fund_result.get('name', symbol)}")
            print(f"  技术置信度: {confidence:.1f}%")
            print(f"  基本面得分: {score}/100")
            print(f"  操作建议: {action}")

            indicators = fund_result.get('indicators', {})
            print(f"\n  关键财务指标:")
            print(f"    ROE: {indicators.get('roe', 0)*100:.1f}%")
            print(f"    毛利率: {indicators.get('gross_margin', 0)*100:.1f}%")
            print(f"    现金流肖像: {indicators.get('cash_flow_portrait', 'N/A')}")

        elif status == '预警':
            print(f"\n! 基本面有瑕疵")
            print(f"  技术置信度: {confidence:.1f}%")
            print(f"  基本面得分: {score}/100")
            print(f"  建议: 谨慎观望")

        else:
            print(f"\n✗ 基本面不达标")
            print(f"  虽然技术面好，但财报有问题")
            print(f"  建议: 不投资")

    except Exception as e:
        print(f"基本面分析失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)
    print("测试完成!")
    print("="*70)


if __name__ == "__main__":
    test_single()
