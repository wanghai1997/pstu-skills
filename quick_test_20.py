# -*- coding: utf-8 -*-
"""
快速测试脚本 - 20只股票

用于快速验证筛选器功能，预计用时 3-5 分钟
"""

import sys
import time

sys.path.insert(0, 'd:\\fuyong\\stu_test\\pstu')

from financial_screener import FinancialScreener
from financial_screener.report_generator import (
    generate_excel_report,
    generate_summary
)

# 20只各行业代表性股票
QUICK_TEST_STOCKS = [
    # 白酒
    "600519",  # 贵州茅台
    "000858",  # 五粮液
    "600809",  # 山西汾酒

    # 消费
    "600887",  # 伊利股份
    "000333",  # 美的集团
    "000651",  # 格力电器
    "603288",  # 海天味业

    # 医药
    "600276",  # 恒瑞医药
    "300760",  # 迈瑞医疗
    "600436",  # 片仔癀

    # 科技
    "002415",  # 海康威视
    "300124",  # 汇川技术
    "603501",  # 韦尔股份

    # 新能源
    "300750",  # 宁德时代
    "601012",  # 隆基绿能
    "002594",  # 比亚迪

    # 金融
    "600036",  # 招商银行
    "601318",  # 中国平安

    # 其他行业
    "601899",  # 紫金矿业
    "600900",  # 长江电力
]


def main():
    print("="*60)
    print("快速测试 - 20只股票")
    print("="*60)
    print(f"\n测试标的: {len(QUICK_TEST_STOCKS)} 只")
    print("预计用时: 3-5 分钟")
    print("\n包含行业: 白酒、消费、医药、科技、新能源、金融")
    print("="*60)

    screener = FinancialScreener(use_cache=True)
    results = []

    start_time = time.time()

    print("\n开始筛选...\n")

    for i, symbol in enumerate(QUICK_TEST_STOCKS, 1):
        print(f"[{i:2d}/{len(QUICK_TEST_STOCKS)}] 分析 {symbol}...", end=" ")

        try:
            result = screener.screen_single(symbol)
            results.append(result)

            # 简洁输出
            status = result['status']
            score = result['score']
            name = result.get('name', symbol)

            if status == '通过':
                print(f"[OK] {name:12s} - 得分: {score:3d} - 现金流: {result.get('indicators', {}).get('cash_flow_portrait', 'N/A')}")
            elif status == '预警':
                print(f"[!] {name:12s} - 得分: {score:3d} - 需关注")
            else:
                print(f"[X] {name:12s} - 得分: {score:3d} - 排除")

        except Exception as e:
            print(f"[错误] {e}")
            results.append({
                'symbol': symbol,
                'name': 'Error',
                'status': '错误',
                'score': 0
            })

        time.sleep(0.5)  # 小间隔

    # 统计
    elapsed = time.time() - start_time
    passed = [r for r in results if r.get('status') == '通过']
    warning = [r for r in results if r.get('status') == '预警']
    excluded = [r for r in results if r.get('status') == '排除']

    print("\n" + "="*60)
    print("筛选完成!")
    print("="*60)
    print(f"\n用时: {elapsed:.1f} 秒")
    print(f"\n结果统计:")
    print(f"  通过: {len(passed):2d} 只 ({len(passed)/len(results)*100:.0f}%)")
    print(f"  预警: {len(warning):2d} 只 ({len(warning)/len(results)*100:.0f}%)")
    print(f"  排除: {len(excluded):2d} 只 ({len(excluded)/len(results)*100:.0f}%)")

    # TOP 5
    print("\n得分 TOP 5:")
    sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
    for i, r in enumerate(sorted_results[:5], 1):
        indicators = r.get('indicators', {})
        roe = indicators.get('roe', 0)
        print(f"  {i}. {r.get('name', 'N/A'):12s} ({r.get('symbol')}) - "
              f"得分: {r.get('score'):3d} | ROE: {roe*100 if roe else 0:5.1f}%")

    # 生成报告
    print("\n生成Excel报告...")
    excel_file = f"quick_test_20_{time.strftime('%Y%m%d_%H%M%S')}.xlsx"
    generate_excel_report(results, excel_file)
    print(f"报告已保存: {excel_file}")

    print("\n" + "="*60)
    print("快速测试完成!")
    print("="*60)
    print(f"\n如果结果正常，可以运行 large_scale_test.py 测试100只以上!")


if __name__ == "__main__":
    main()
