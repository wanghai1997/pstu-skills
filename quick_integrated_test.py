# -*- coding: utf-8 -*-
"""
整合选股系统 - 快速测试（非交互式）

直接运行20只股票的测试，无需交互输入
"""

import sys
import time

sys.path.insert(0, 'd:\\fuyong\\stu_test\\pstu')

from investment_master import MasterAnalyzer
from financial_screener import FinancialScreener


class QuickIntegratedTest:
    """快速整合测试"""

    def __init__(self):
        self.master_analyzer = MasterAnalyzer()
        self.financial_screener = FinancialScreener()

    def run_test(self, symbols, min_confidence=65):
        """运行测试"""
        print("="*70)
        print("整合选股系统 - 快速测试")
        print("="*70)
        print(f"\n测试标的: {len(symbols)} 只股票")
        print("选股逻辑: 技术面初选 → 基本面确认")
        print(f"技术筛选阈值: 置信度 ≥ {min_confidence}%")
        print("="*70)

        start_time = time.time()

        # ========== 第一阶段：技术面筛选 ==========
        print("\n" + "="*70)
        print("【第一阶段】技术面筛选 - 投资大师分析系统")
        print("="*70)

        technical_passed = []
        watch_list = []

        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i:2d}/{len(symbols)}] 分析 {symbol}...", end=" ")

            try:
                result = self.master_analyzer.analyze(symbol)
                confidence = result.get('confidence', 0)

                if confidence >= min_confidence:
                    status_icon = "[通过]"
                    print(f"{status_icon} 置信度: {confidence:.1f}% - {result.get('action', '未知')}")
                    technical_passed.append({
                        'symbol': symbol,
                        'name': result.get('name', symbol),
                        'confidence': confidence,
                        'action': result.get('action', '未知'),
                        'position': result.get('position', ''),
                    })
                elif confidence >= 50:
                    print(f"[观察] 置信度: {confidence:.1f}%")
                    watch_list.append({'symbol': symbol, 'confidence': confidence})
                else:
                    print(f"[排除] 置信度: {confidence:.1f}%")

                time.sleep(0.3)

            except Exception as e:
                print(f"[错误] {str(e)[:50]}")

        # 技术面结果汇总
        print("\n" + "="*70)
        print("【第一阶段完成】技术面筛选结果")
        print("="*70)
        print(f"通过技术筛选: {len(technical_passed)} 只")
        print(f"观察列表: {len(watch_list)} 只")
        print(f"排除: {len(symbols) - len(technical_passed) - len(watch_list)} 只")

        if technical_passed:
            print("\n技术面通过的股票（按置信度排序）:")
            technical_passed.sort(key=lambda x: x['confidence'], reverse=True)
            for i, stock in enumerate(technical_passed, 1):
                print(f"  {i:2d}. {stock['name']:12s} ({stock['symbol']}) - "
                      f"置信度: {stock['confidence']:5.1f}% | {stock['action']}")

        if not technical_passed:
            print("\n没有股票通过技术面筛选，测试结束")
            return None

        # ========== 第二阶段：基本面筛选 ==========
        print("\n" + "="*70)
        print("【第二阶段】基本面筛选 - 财报筛选器")
        print("="*70)
        print(f"待确认股票: {len(technical_passed)} 只")

        double_confirmed = []
        fundamental_warnings = []

        for i, stock in enumerate(technical_passed, 1):
            symbol = stock['symbol']
            print(f"\n[{i:2d}/{len(technical_passed)}] 财报分析 {symbol} ({stock['name']})...")

            try:
                result = self.financial_screener.screen_single(symbol)
                status = result.get('status', '未知')

                integrated_result = {
                    'symbol': symbol,
                    'name': result.get('name', stock['name']),
                    'technical_confidence': stock['confidence'],
                    'technical_action': stock['action'],
                    'technical_position': stock['position'],
                    'fundamental_status': status,
                    'fundamental_score': result.get('score', 0),
                    'indicators': result.get('indicators', {}),
                    'warnings': result.get('warnings', []),
                }

                if status == '通过':
                    print(f"  [✓ 双重确认] 技术面优秀 + 基本面健康")
                    double_confirmed.append(integrated_result)
                elif status == '预警':
                    print(f"  [! 需关注] 基本面有瑕疵")
                    fundamental_warnings.append(integrated_result)
                else:
                    print(f"  [✗ 排除] 基本面不达标")

                time.sleep(0.5)

            except Exception as e:
                print(f"  [错误] {str(e)[:50]}")

        # ========== 最终结果汇总 ==========
        elapsed = time.time() - start_time

        print("\n" + "="*70)
        print("【选股完成】最终结果")
        print("="*70)
        print(f"\n总用时: {elapsed/60:.1f} 分钟")
        print(f"\n原始候选: {len(symbols)} 只股票")
        print(f"├─ 技术面通过: {len(technical_passed)} 只")
        print(f"│  ├─ ✓ 双重确认: {len(double_confirmed)} 只")
        print(f"│  ├─ ! 基本面预警: {len(fundamental_warnings)} 只")
        print(f"│  └─ ✗ 基本面排除: {len(technical_passed) - len(double_confirmed) - len(fundamental_warnings)} 只")
        print(f"└─ 技术面排除/观察: {len(symbols) - len(technical_passed)} 只")

        # 显示投资观察池
        if double_confirmed:
            print("\n" + "="*70)
            print("【投资观察池】双重确认的股票")
            print("="*70)

            double_confirmed.sort(key=lambda x: x['technical_confidence'], reverse=True)

            for i, stock in enumerate(double_confirmed, 1):
                indicators = stock.get('indicators', {})

                print(f"\n{i}. {stock['name']} ({stock['symbol']})")
                print(f"   技术置信度: {stock['technical_confidence']:.1f}%")
                print(f"   操作建议: {stock['technical_action']} | 仓位: {stock['technical_position']}")
                print(f"   基本面得分: {stock['fundamental_score']}/100")
                print(f"   关键指标: ROE {indicators.get('roe', 0)*100:.1f}% | "
                      f"毛利率 {indicators.get('gross_margin', 0)*100:.1f}% | "
                      f"现金流: {indicators.get('cash_flow_portrait', 'N/A')}")

        # 显示基本面有瑕疵的
        if fundamental_warnings:
            print("\n" + "="*70)
            print("【需谨慎】技术面好但基本面有瑕疵")
            print("="*70)
            for stock in fundamental_warnings:
                print(f"  ! {stock['name']} ({stock['symbol']}) - "
                      f"置信度: {stock['technical_confidence']:.1f}% - "
                      f"基本面得分: {stock['fundamental_score']}")
                for warning in stock.get('warnings', [])[:2]:
                    print(f"      - {warning}")

        # 生成Excel报告
        self._generate_report(double_confirmed, fundamental_warnings)

        return {
            'double_confirmed': double_confirmed,
            'warnings': fundamental_warnings,
            'technical_passed': technical_passed,
        }

    def _generate_report(self, double_confirmed, warnings):
        """生成Excel报告"""
        try:
            import pandas as pd
            from datetime import datetime

            report_data = []

            # 双重确认的股票
            for stock in double_confirmed:
                indicators = stock.get('indicators', {})
                report_data.append({
                    '股票代码': stock['symbol'],
                    '股票名称': stock['name'],
                    '综合评级': '✓ 双重确认',
                    '技术置信度': f"{stock['technical_confidence']:.1f}%",
                    '基本面得分': stock['fundamental_score'],
                    '操作建议': stock['technical_action'],
                    '仓位建议': stock['technical_position'],
                    'ROE': f"{indicators.get('roe', 0)*100:.1f}%",
                    '毛利率': f"{indicators.get('gross_margin', 0)*100:.1f}%",
                    '现金流肖像': indicators.get('cash_flow_portrait', 'N/A'),
                })

            # 基本面有瑕疵的
            for stock in warnings:
                report_data.append({
                    '股票代码': stock['symbol'],
                    '股票名称': stock['name'],
                    '综合评级': '! 基本面预警',
                    '技术置信度': f"{stock['technical_confidence']:.1f}%",
                    '基本面得分': stock['fundamental_score'],
                    '操作建议': '谨慎观望',
                    '仓位建议': '不超过10%',
                    'ROE': '-',
                    '毛利率': '-',
                    '现金流肖像': '-',
                })

            if report_data:
                df = pd.DataFrame(report_data)
                filename = f"integrated_picking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df.to_excel(filename, index=False)
                print(f"\n\nExcel报告已保存: {filename}")

        except Exception as e:
            print(f"\n生成报告时出错: {e}")


def main():
    """主函数"""
    # 20只测试股票
    symbols = [
        "600519", "000858", "600809", "000333", "600887",  # 消费
        "600276", "300760", "600436", "002415", "300124",  # 医药科技
        "300750", "601012", "002594", "600036", "601318",  # 新能源金融
        "601899", "600900", "603288", "000651", "603501",  # 其他
    ]

    test = QuickIntegratedTest()
    test.run_test(symbols, min_confidence=65)

    print("\n" + "="*70)
    print("测试完成!")
    print("="*70)


if __name__ == "__main__":
    main()
