# -*- coding: utf-8 -*-
"""
分析通过财报筛选的股票（技术面分析）

流程：读取财报筛选结果 → 用投资大师系统进行技术面分析 → 生成综合报告

使用方法:
    python analyze_passed_stocks.py
"""

import os
import sys
import time
import pandas as pd

sys.path.insert(0, '.')

from investment_master import MasterAnalyzer
from financial_screener.report_generator import generate_excel_report


def load_passed_symbols():
    """
    从财报筛选结果Excel文件中读取通过筛选的股票代码

    优先读取最新的筛选结果，如果失败则使用默认列表
    """
    excel_files = [
        '筛选结果_沪深300.xlsx',  # 优先读取沪深300筛选结果
        '筛选结果_全市场.xlsx',    # 备选：全市场筛选结果
        '筛选结果_默认5只.xlsx',   # 备选：默认测试列表
    ]

    for filename in excel_files:
        try:
            if os.path.exists(filename):
                df = pd.read_excel(filename)
                # 筛选状态为"通过"的股票
                status_col = None
                for col in df.columns:
                    if col in ['状态', 'status', '筛选状态']:
                        status_col = col
                        break

                if status_col:
                    passed = df[df[status_col] == '通过']
                else:
                    # 如果没有状态列，假设全部是通过的
                    passed = df

                # 获取股票代码列
                code_col = None
                for col in passed.columns:
                    if '代码' in col or col.lower() == 'symbol':
                        code_col = col
                        break

                if not code_col:
                    continue

                # 读取股票代码并统一格式为6位字符串
                symbols = passed[code_col].astype(str).str.strip().tolist()
                # 清理代码格式（去掉可能的 .SZ/.SH 后缀，并补零到6位）
                symbols = [s.split('.')[0].zfill(6) for s in symbols]

                print(f"[OK] 从 {filename} 读取了 {len(symbols)} 只通过筛选的股票")
                return symbols
        except Exception as e:
            print(f"[WARN] 读取 {filename} 失败: {e}")
            continue

    # 如果所有文件都读取失败，使用默认列表
    print("[WARN] 未能从Excel读取筛选结果，使用默认列表")
    return []


def analyze_passed_stocks():
    """分析通过财报筛选的股票"""
    print("=" * 80)
    print("投资大师系统 - 技术面分析")
    print("=" * 80)

    # 从Excel文件读取本次筛选结果
    passed_symbols = load_passed_symbols()

    if not passed_symbols:
        print("[错误] 没有找到通过筛选的股票，请先运行: python run_screener.py --hs300")
        return

    print(f"\n分析对象: 通过财报筛选的 {len(passed_symbols)} 只股票")
    print("\n分析维度:")
    print("  - 多周期趋势一致性（周线/日线/60分钟/15分钟）")
    print("  - 技术形态评估（均线系统、MACD、KDJ）")
    print("  - 动量强度分析")
    print("  - 量价配合情况")
    print("  - 综合置信度评分")
    print("=" * 80)

    # 初始化投资大师分析器
    analyzer = MasterAnalyzer()

    # 存储分析结果
    results = []

    for i, symbol in enumerate(passed_symbols, 1):
        print(f"\n[{i:2d}/{len(passed_symbols)}] 分析 {symbol}...", end=" ")

        try:
            result = analyzer.analyze(symbol)
            confidence = result.get('confidence', 0)
            action = result.get('action', '未知')
            position = result.get('position', '')

            print(f"置信度: {confidence:5.1f}% | 建议: {action} | 仓位: {position}")

            # 整理结果
            results.append({
                'symbol': symbol,
                'name': result.get('name', symbol),
                'confidence': confidence,
                'action': action,
                'position': position,
                'trend_daily': result.get('trend', {}).get('daily', '未知'),
                'trend_weekly': result.get('trend', {}).get('weekly', '未知'),
                'trend_60min': result.get('trend', {}).get('min60', '未知'),
                'trend_15min': result.get('trend', {}).get('min15', '未知'),
                'technical_score': result.get('technical_score', 0),
                'risk_level': result.get('risk_level', '未知'),
            })

            # 间隔，避免请求过快
            time.sleep(0.3)

        except Exception as e:
            print(f"[错误] {e}")
            results.append({
                'symbol': symbol,
                'name': '分析失败',
                'confidence': 0,
                'action': '错误',
                'position': '',
            })

    # 生成汇总报告
    print("\n" + "=" * 80)
    print("分析完成 - 汇总报告")
    print("=" * 80)

    # 按置信度排序
    results.sort(key=lambda x: x.get('confidence', 0), reverse=True)

    # 分类统计
    strong_buy = [r for r in results if r.get('confidence', 0) >= 70]
    buy = [r for r in results if 55 <= r.get('confidence', 0) < 70]
    watch = [r for r in results if 40 <= r.get('confidence', 0) < 55]
    avoid = [r for r in results if r.get('confidence', 0) < 40]

    print(f"\n技术面分类统计:")
    print(f"  强烈建议买入 (≥70%): {len(strong_buy)} 只")
    print(f"  建议买入 (55-70%):   {len(buy)} 只")
    print(f"  继续观察 (40-55%):   {len(watch)} 只")
    print(f"  暂时回避 (<40%):     {len(avoid)} 只")

    # 显示强烈建议买入的股票
    if strong_buy:
        print(f"\n强烈建议买入的股票 (置信度≥70%):")
        print("-" * 80)
        for i, r in enumerate(strong_buy[:10], 1):
            print(f"  {i:2d}. {r['name']:12s} ({r['symbol']}) - "
                  f"置信度: {r['confidence']:5.1f}% | "
                  f"建议: {r['action']:10s} | "
                  f"日线趋势: {r.get('trend_daily', '未知')}")

    # 显示建议买入的股票
    if buy:
        print(f"\n建议买入的股票 (置信度55-70%):")
        print("-" * 80)
        for i, r in enumerate(buy[:10], 1):
            print(f"  {i:2d}. {r['name']:12s} ({r['symbol']}) - "
                  f"置信度: {r['confidence']:5.1f}% | "
                  f"建议: {r['action']:10s}")

    # 生成Excel报告
    generate_excel(results, len(passed_symbols))

    print("\n" + "=" * 80)
    print("分析完成!")
    print("=" * 80)


def generate_excel(results, count=None):
    """生成Excel报告"""
    try:
        import pandas as pd
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment

        df = pd.DataFrame(results)

        # 重命名列
        df = df.rename(columns={
            'symbol': '股票代码',
            'name': '股票名称',
            'confidence': '置信度(%)',
            'action': '操作建议',
            'position': '建议仓位',
            'trend_daily': '日线趋势',
            'trend_weekly': '周线趋势',
            'trend_60min': '60分钟趋势',
            'trend_15min': '15分钟趋势',
            'technical_score': '技术评分',
            'risk_level': '风险等级',
        })

        # 按置信度排序
        df = df.sort_values('置信度(%)', ascending=False)

        # 保存到Excel（文件名根据实际股票数量动态生成）
        count = count or len(results)
        filename = f'投资大师分析_{count}只财报通过股票.xlsx'
        df.to_excel(filename, index=False, engine='openpyxl')

        print(f"\n[OK] Excel报告已生成: {filename}")

    except Exception as e:
        print(f"\n[WARN] Excel报告生成失败: {e}")


if __name__ == "__main__":
    try:
        analyze_passed_stocks()
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消分析")
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
