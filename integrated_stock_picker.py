# -*- coding: utf-8 -*-
"""
整合选股系统

流程：先用投资大师分析系统（技术面）初选 → 再用财报筛选器（基本面）确认

使用逻辑：
1. 先用技术分析找出"有机会"的股票（趋势好、形态佳、置信度高）
2. 再用财报筛选器确认"基本面健康"（排雷）
3. 双重确认后进入投资观察池
"""

import sys
import time

sys.path.insert(0, 'd:\\fuyong\\stu_test\\pstu')

from investment_master import MasterAnalyzer
from financial_screener import FinancialScreener
from financial_screener.report_generator import generate_excel_report


class IntegratedStockPicker:
    """
    整合选股器

    结合技术面分析和基本面筛选的两阶段选股系统
    """

    def __init__(self):
        self.master_analyzer = MasterAnalyzer()  # 投资大师系统（技术面）
        self.financial_screener = FinancialScreener()  # 财报筛选器（基本面）

    def stage1_technical_screening(self, symbols, min_confidence=65):
        """
        第一阶段：技术面筛选

        使用投资大师分析系统，筛选出置信度高的股票

        Args:
            symbols: 候选股票列表
            min_confidence: 最小置信度阈值（默认65%，即"买入"级别）

        Returns:
            list: 通过技术筛选的股票
        """
        print("\n" + "="*70)
        print("【第一阶段】技术面筛选 - 投资大师分析系统")
        print("="*70)
        print(f"\n候选股票: {len(symbols)} 只")
        print(f"筛选标准: 置信度 ≥ {min_confidence}%")
        print("\n此阶段关注：")
        print("  - 多周期趋势是否一致（周线/日线/60分钟/15分钟）")
        print("  - 技术形态是否良好（均线排列、MACD、KDJ）")
        print("  - 量价配合是否合理")
        print("  - 动量强度是否足够")

        passed = []
        watch_list = []

        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i:3d}/{len(symbols)}] 分析 {symbol}...", end=" ")

            try:
                result = self.master_analyzer.analyze(symbol)
                confidence = result.get('confidence', 0)

                if confidence >= min_confidence:
                    print(f"[通过] 置信度: {confidence:.1f}% - {result.get('action', '未知')}")
                    passed.append({
                        'symbol': symbol,
                        'name': result.get('name', symbol),
                        'confidence': confidence,
                        'action': result.get('action', '未知'),
                        'position': result.get('position', ''),
                        'technical_details': result
                    })
                elif confidence >= 50:
                    print(f"[观察] 置信度: {confidence:.1f}% - 趋势尚可但不够强")
                    watch_list.append({
                        'symbol': symbol,
                        'name': result.get('name', symbol),
                        'confidence': confidence,
                        'action': result.get('action', '未知')
                    })
                else:
                    print(f"[排除] 置信度: {confidence:.1f}% - 技术面不佳")

                # 小间隔，避免请求过快
                time.sleep(0.5)

            except Exception as e:
                print(f"[错误] {e}")

        print("\n" + "="*70)
        print("【第一阶段完成】技术面筛选结果")
        print("="*70)
        print(f"\n通过技术筛选: {len(passed)} 只")
        print(f"观察列表: {len(watch_list)} 只")
        print(f"排除: {len(symbols) - len(passed) - len(watch_list)} 只")

        if passed:
            print("\n技术面通过的股票（按置信度排序）:")
            passed.sort(key=lambda x: x['confidence'], reverse=True)
            for i, stock in enumerate(passed[:10], 1):
                print(f"  {i:2d}. {stock['name']:12s} ({stock['symbol']}) - "
                      f"置信度: {stock['confidence']:5.1f}% | "
                      f"建议: {stock['action']}")

        return passed, watch_list

    def stage2_fundamental_screening(self, technical_passed):
        """
        第二阶段：基本面筛选

        使用财报筛选器，排除财务有问题的股票

        Args:
            technical_passed: 第一阶段通过的股票列表

        Returns:
            list: 双重确认的股票
        """
        print("\n" + "="*70)
        print("【第二阶段】基本面筛选 - 财报筛选器")
        print("="*70)
        print(f"\n待确认股票: {len(technical_passed)} 只（技术面通过）")
        print("\n此阶段关注：")
        print("  - ROE ≥ 15%（盈利能力）")
        print("  - 毛利率 ≥ 20%（产品竞争力）")
        print("  - 应收账款/总资产 ≤ 30%（回款能力）")
        print("  - 现金流质量（经营现金流/净利润 ≥ 0.5）")
        print("  - 现金流肖像（奶牛型+--最理想）")

        double_confirmed = []
        fundamental_warnings = []
        fundamental_excluded = []

        for i, stock in enumerate(technical_passed, 1):
            symbol = stock['symbol']
            print(f"\n[{i:2d}/{len(technical_passed)}] 财报分析 {symbol} ({stock['name']})...")

            try:
                result = self.financial_screener.screen_single(symbol)
                status = result.get('status', '未知')

                # 整合两个阶段的结果
                integrated_result = {
                    'symbol': symbol,
                    'name': result.get('name', stock['name']),
                    'technical': {
                        'confidence': stock['confidence'],
                        'action': stock['action'],
                        'position': stock['position'],
                    },
                    'fundamental': {
                        'status': status,
                        'score': result.get('score', 0),
                        'indicators': result.get('indicators', {}),
                        'warnings': result.get('warnings', []),
                        'exclusions': result.get('exclusions', []),
                    },
                    'checks': result.get('checks', {}),
                }

                if status == '通过':
                    print(f"  [OK 双重确认] 技术面优秀 + 基本面健康")
                    double_confirmed.append(integrated_result)
                elif status == '预警':
                    print(f"  [! 需关注] 技术面优秀但基本面有瑕疵")
                    fundamental_warnings.append(integrated_result)
                else:  # 排除
                    print(f"  [X 排除] 基本面不达标")
                    fundamental_excluded.append(integrated_result)

                time.sleep(1)  # 避免请求过快

            except Exception as e:
                print(f"  [错误] 分析失败: {e}")

        return double_confirmed, fundamental_warnings, fundamental_excluded

    def pick_stocks(self, symbols, min_confidence=65):
        """
        完整选股流程

        Args:
            symbols: 候选股票列表
            min_confidence: 技术面最小置信度

        Returns:
            dict: 各阶段结果
        """
        start_time = time.time()

        # 第一阶段：技术面筛选
        technical_passed, watch_list = self.stage1_technical_screening(
            symbols, min_confidence
        )

        if not technical_passed:
            print("\n【选股完成】没有股票通过技术面筛选")
            return {
                'double_confirmed': [],
                'technical_passed': [],
                'watch_list': watch_list,
            }

        # 第二阶段：基本面筛选
        double_confirmed, warnings, excluded = self.stage2_fundamental_screening(
            technical_passed
        )

        # 生成最终报告
        elapsed = time.time() - start_time

        print("\n" + "="*70)
        print("【选股完成】最终结果")
        print("="*70)
        print(f"\n总用时: {elapsed/60:.1f} 分钟")
        print(f"\n原始候选: {len(symbols)} 只股票")
        print(f"+- 技术面通过: {len(technical_passed)} 只")
        print(f"|  +- [OK] 双重确认: {len(double_confirmed)} 只 (进入投资观察池)")
        print(f"|  +- [!] 基本面预警: {len(warnings)} 只 (需谨慎)")
        print(f"|  +- [X] 基本面排除: {len(excluded)} 只 (财务有问题)")
        print(f"+- 技术面观察: {len(watch_list)} 只")

        if double_confirmed:
            print("\n" + "="*70)
            print("【投资观察池】双重确认的股票")
            print("="*70)

            # 按技术面置信度排序
            double_confirmed.sort(
                key=lambda x: x['technical']['confidence'],
                reverse=True
            )

            for i, stock in enumerate(double_confirmed, 1):
                tech = stock['technical']
                fund = stock['fundamental']
                indicators = fund.get('indicators', {})

                print(f"\n{i}. {stock['name']} ({stock['symbol']})")
                print(f"   技术面置信度: {tech['confidence']:.1f}%")
                print(f"   操作建议: {tech['action']} | 仓位: {tech['position']}")
                print(f"   基本面得分: {fund['score']}/100")
                print(f"   关键指标: ROE {indicators.get('roe', 0)*100:.1f}% | "
                      f"毛利率 {indicators.get('gross_margin', 0)*100:.1f}% | "
                      f"现金流: {indicators.get('cash_flow_portrait', 'N/A')}")

        return {
            'double_confirmed': double_confirmed,
            'fundamental_warnings': warnings,
            'fundamental_excluded': excluded,
            'technical_passed': technical_passed,
            'watch_list': watch_list,
        }


def main():
    """
    主函数
    """
    print("="*70)
    print("整合选股系统")
    print("="*70)
    print("\n选股逻辑:")
    print("  1. 先用【投资大师系统】技术面初选（趋势、形态、动量）")
    print("  2. 再用【财报筛选器】基本面确认（排雷、验证）")
    print("\n双重确认的股票进入【投资观察池】")
    print("="*70)

    # 创建选股器
    picker = IntegratedStockPicker()

    # 选择测试范围
    print("\n请选择测试范围:")
    print("1. 快速测试 (20只股票，约15-20分钟)")
    print("2. 中等规模 (50只股票，约40-50分钟)")
    print("3. 大规模测试 (100只股票，约1.5-2小时)")

    choice = input("\n请输入选择 (1/2/3): ").strip()

    if choice == '1':
        # 20只快速测试
        symbols = [
            "600519", "000858", "600809", "000333", "600887",  # 消费
            "600276", "300760", "600436", "002415", "300124",  # 医药科技
            "300750", "601012", "002594", "600036", "601318",  # 新能源金融
            "601899", "600900", "603288", "000651", "603501",  # 其他
        ]
    elif choice == '2':
        # 50只
        symbols = [
            # 消费20只
            "600519", "000858", "600809", "000568", "002304", "600887", "603288",
            "002507", "603345", "000333", "000651", "600690", "002032", "603486",
            "603195", "600315", "603605", "002511", "300999", "600298",
            # 医药15只
            "600276", "000538", "300760", "603259", "300015", "300122", "600436",
            "000963", "300003", "002001", "600079", "603392", "300347", "600763", "300142",
            # 科技15只
            "002415", "000725", "603501", "300124", "002371", "688012", "603986",
            "300408", "002049", "300661", "688008", "603893", "300782", "002236", "688981",
        ]
    elif choice == '3':
        # 100只
        from large_scale_test import LARGE_CAP_STOCKS
        symbols = LARGE_CAP_STOCKS
    else:
        print("无效选择，使用默认20只")
        symbols = ["600519", "000858", "600276", "300750", "002415", "601318",
                   "600036", "000333", "601012", "002594"]

    print(f"\n将测试 {len(symbols)} 只股票")
    print("技术面筛选阈值: 置信度 ≥ 65%")

    confirm = input("\n确认开始? (y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return

    # 执行选股
    results = picker.pick_stocks(symbols, min_confidence=65)

    # 生成报告
    if results['double_confirmed'] or results['fundamental_warnings']:
        print("\n" + "="*70)
        print("正在生成Excel报告...")
        print("="*70)

        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # 准备报告数据
        report_data = []

        # 双重确认的股票
        for stock in results['double_confirmed']:
            tech = stock['technical']
            fund = stock['fundamental']
            indicators = fund.get('indicators', {})

            report_data.append({
                '股票代码': stock['symbol'],
                '股票名称': stock['name'],
                '综合评级': '✓ 双重确认',
                '技术置信度': f"{tech['confidence']:.1f}%",
                '基本面得分': fund['score'],
                '操作建议': tech['action'],
                '仓位建议': tech['position'],
                'ROE': f"{indicators.get('roe', 0)*100:.1f}%",
                '毛利率': f"{indicators.get('gross_margin', 0)*100:.1f}%",
                '现金流肖像': indicators.get('cash_flow_portrait', 'N/A'),
            })

        # 基本面有瑕疵的
        for stock in results['fundamental_warnings']:
            tech = stock['technical']
            fund = stock['fundamental']

            report_data.append({
                '股票代码': stock['symbol'],
                '股票名称': stock['name'],
                '综合评级': '! 基本面预警',
                '技术置信度': f"{tech['confidence']:.1f}%",
                '基本面得分': fund['score'],
                '操作建议': '谨慎观望',
                '仓位建议': '不超过10%',
                'ROE': '-',
                '毛利率': '-',
                '现金流肖像': '-',
            })

        # 保存Excel
        import pandas as pd
        df = pd.DataFrame(report_data)
        excel_file = f"integrated_picking_{timestamp}.xlsx"
        df.to_excel(excel_file, index=False)

        print(f"\n报告已保存: {excel_file}")

    print("\n" + "="*70)
    print("选股流程全部完成!")
    print("="*70)


if __name__ == "__main__":
    main()
