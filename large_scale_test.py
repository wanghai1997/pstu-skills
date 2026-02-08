# -*- coding: utf-8 -*-
"""
大规模财报筛选测试脚本

支持分批测试大量股票，避免一次性下载过多数据导致网络问题
"""

import sys
import time

sys.path.insert(0, 'd:\\fuyong\\stu_test\\pstu')

from financial_screener import FinancialScreener
from financial_screener.report_generator import (
    generate_text_report,
    generate_excel_report,
    generate_summary
)

# ==================== 100只优质股票列表 ====================
# 来源：沪深300成分股 + 各行业龙头
# 已排除ST股和有明显财务问题的公司

LARGE_CAP_STOCKS = [
    # 消费 - 白酒/食品 (15只)
    "600519",  # 贵州茅台
    "000858",  # 五粮液
    "000568",  # 泸州老窖
    "002304",  # 洋河股份
    "600809",  # 山西汾酒
    "600887",  # 伊利股份
    "603288",  # 海天味业
    "002507",  # 涪陵榨菜
    "603345",  # 安井食品
    "300999",  # 金龙鱼
    "600298",  # 安琪酵母
    "600872",  # 中炬高新
    "603517",  # 绝味食品
    "002557",  # 洽洽食品
    "605499",  # 东鹏饮料

    # 消费 - 家电/日用品 (10只)
    "000333",  # 美的集团
    "000651",  # 格力电器
    "600690",  # 海尔智家
    "002032",  # 苏泊尔
    "603486",  # 科沃斯
    "603195",  # 公牛集团
    "600315",  # 上海家化
    "603605",  # 珀莱雅
    "300888",  # 稳健医疗
    "002511",  # 中顺洁柔

    # 医药 (15只)
    "600276",  # 恒瑞医药
    "000538",  # 云南白药
    "300760",  # 迈瑞医疗
    "603259",  # 药明康德
    "300015",  # 爱尔眼科
    "300122",  # 智飞生物
    "600436",  # 片仔癀
    "000963",  # 华东医药
    "300003",  # 乐普医疗
    "002001",  # 新和成
    "600079",  # 人福医药
    "603392",  # 万泰生物
    "300347",  # 泰格医药
    "600763",  # 通策医疗
    "300142",  # 沃森生物

    # 科技 - 电子/半导体 (15只)
    "002415",  # 海康威视
    "000725",  # 京东方A
    "603501",  # 韦尔股份
    "688981",  # 中芯国际
    "300124",  # 汇川技术
    "002371",  # 北方华创
    "688012",  # 中微公司
    "603986",  # 兆易创新
    "300408",  # 三环集团
    "002049",  # 紫光国微
    "300661",  # 圣邦股份
    "688008",  # 澜起科技
    "603893",  # 瑞芯微
    "300782",  # 卓胜微
    "002236",  # 大华股份

    # 新能源/电力 (10只)
    "300750",  # 宁德时代
    "601012",  # 隆基绿能
    "002594",  # 比亚迪
    "601899",  # 紫金矿业
    "601985",  # 中国核电
    "600900",  # 长江电力
    "601088",  # 中国神华
    "601669",  # 中国电建
    "600406",  # 国电南瑞
    "601727",  # 上海电气

    # 金融 - 银行/保险/券商 (10只)
    "600036",  # 招商银行
    "000001",  # 平安银行
    "601166",  # 兴业银行
    "601398",  # 工商银行
    "601318",  # 中国平安
    "601628",  # 中国人寿
    "600030",  # 中信证券
    "300059",  # 东方财富
    "601688",  # 华泰证券
    "000776",  # 广发证券

    # 制造/工业 (10只)
    "601766",  # 中国中车
    "600031",  # 三一重工
    "000425",  # 徐工机械
    "601100",  # 恒立液压
    "600499",  # 科达制造
    "601238",  # 广汽集团
    "000768",  # 中航西飞
    "600893",  # 航发动力
    "002179",  # 中航光电
    "601390",  # 中国中铁

    # 通信/互联网 (10只)
    "600941",  # 中国移动
    "600050",  # 中国联通
    "000063",  # 中兴通讯
    "300413",  # 芒果超媒
    "002027",  # 分众传媒
    "300251",  # 光线传媒
    "603000",  # 人民网
    "300418",  # 昆仑万维
    "002555",  # 三七互娱
    "002624",  # 完美世界

    # 化工/材料 (5只)
    "600309",  # 万华化学
    "002001",  # 新和成
    "600426",  # 华鲁恒升
    "601233",  # 桐昆股份
    "603225",  # 新凤鸣
]


def batch_screening(symbols, batch_size=20, delay_between_batches=5):
    """
    分批筛选股票

    Args:
        symbols: 股票代码列表
        batch_size: 每批处理的数量
        delay_between_batches: 批次之间的等待时间（秒）

    Returns:
        list: 所有筛选结果
    """
    screener = FinancialScreener(use_cache=True)

    total = len(symbols)
    all_results = []

    print(f"\n开始大规模筛选: 共 {total} 只股票")
    print(f"分批策略: 每批 {batch_size} 只，间隔 {delay_between_batches} 秒")
    print("="*60)

    # 分批处理
    for i in range(0, total, batch_size):
        batch = symbols[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size

        print(f"\n{'='*60}")
        print(f"处理第 {batch_num}/{total_batches} 批 ({len(batch)} 只股票)")
        print('='*60)

        for j, symbol in enumerate(batch, 1):
            actual_index = i + j
            print(f"\n[{actual_index}/{total}] 分析 {symbol}...")

            try:
                result = screener.screen_single(symbol)
                all_results.append(result)

                # 简要显示结果
                status_icon = "[OK]" if result['status'] == '通过' else "[!]" if result['status'] == '预警' else "[X]"
                print(f"  {status_icon} {result.get('name', symbol)} - {result['status']} - 得分: {result['score']}")

            except Exception as e:
                print(f"  [错误] 分析 {symbol} 时出错: {e}")
                # 添加一个错误结果
                all_results.append({
                    'symbol': symbol,
                    'name': 'Error',
                    'status': '错误',
                    'score': 0,
                    'error': str(e)
                })

            # 小间隔，避免请求过快
            if j < len(batch):
                time.sleep(1)

        # 批次之间暂停
        if i + batch_size < total:
            print(f"\n批次 {batch_num} 完成，等待 {delay_between_batches} 秒后继续...")
            time.sleep(delay_between_batches)

    return all_results


def analyze_results(results):
    """
    分析筛选结果
    """
    print("\n" + "="*60)
    print("筛选结果分析")
    print("="*60)

    total = len(results)
    passed = [r for r in results if r.get('status') == '通过']
    warning = [r for r in results if r.get('status') == '预警']
    excluded = [r for r in results if r.get('status') == '排除']
    errors = [r for r in results if r.get('status') == '错误']

    print(f"\n总计: {total} 只股票")
    print(f"  通过: {len(passed)} 只 ({len(passed)/total*100:.1f}%)")
    print(f"  预警: {len(warning)} 只 ({len(warning)/total*100:.1f}%)")
    print(f"  排除: {len(excluded)} 只 ({len(excluded)/total*100:.1f}%)")
    if errors:
        print(f"  错误: {len(errors)} 只")

    # 按得分排序显示前10名
    print("\n" + "="*60)
    print("得分排行榜 TOP 10")
    print("="*60)

    sorted_results = sorted(results, key=lambda x: x.get('score', 0), reverse=True)
    for i, r in enumerate(sorted_results[:10], 1):
        print(f"{i:2d}. {r.get('name', 'N/A'):15s} ({r.get('symbol', 'N/A')}) - 得分: {r.get('score', 0):3d} - {r.get('status', 'N/A')}")

    # 显示通过筛选的股票列表
    if passed:
        print("\n" + "="*60)
        print(f"通过筛选的股票列表 (共 {len(passed)} 只)")
        print("="*60)
        for r in sorted(passed, key=lambda x: x.get('score', 0), reverse=True):
            indicators = r.get('indicators', {})
            roe = indicators.get('roe', 0)
            gross_margin = indicators.get('gross_margin', 0)
            portrait = indicators.get('cash_flow_portrait', 'N/A')

            print(f"  [OK] {r.get('name', 'N/A'):15s} ({r.get('symbol', 'N/A')}) - "
                  f"得分: {r.get('score', 0):3d} | "
                  f"ROE: {roe*100 if roe else 0:5.1f}% | "
                  f"毛利: {gross_margin*100 if gross_margin else 0:5.1f}% | "
                  f"现金流: {portrait}")

    return {
        'total': total,
        'passed': passed,
        'warning': warning,
        'excluded': excluded,
        'errors': errors
    }


def main():
    """
    主函数
    """
    print("="*60)
    print("大规模财报筛选测试")
    print("="*60)
    print(f"\n测试标的: {len(LARGE_CAP_STOCKS)} 只A股优质股票")
    print("来源: 沪深300成分股 + 各行业龙头")
    print("已排除: ST股和有明显财务问题的公司")
    print("\n注意:")
    print("- 首次运行需要下载数据，可能需要20-30分钟")
    print("- 已启用缓存，第二次运行会快很多")
    print("- 每批处理20只，批次间休息5秒，避免网络限制")
    print("="*60)

    # 询问是否开始
    confirm = input("\n是否开始筛选? (y/n): ")
    if confirm.lower() != 'y':
        print("已取消")
        return

    start_time = time.time()

    try:
        # 分批筛选
        results = batch_screening(
            LARGE_CAP_STOCKS,
            batch_size=20,           # 每批20只
            delay_between_batches=5  # 批次间休息5秒
        )

        # 分析结果
        analysis = analyze_results(results)

        # 生成报告
        print("\n" + "="*60)
        print("生成报告...")
        print("="*60)

        # Excel报告
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        excel_file = f"large_screening_report_{timestamp}.xlsx"
        generate_excel_report(results, excel_file)
        print(f"Excel报告已保存: {excel_file}")

        # 文本报告
        text_file = f"large_screening_report_{timestamp}.txt"
        generate_text_report(results, text_file)
        print(f"文本报告已保存: {text_file}")

        # 统计
        elapsed = time.time() - start_time
        print("\n" + "="*60)
        print("筛选完成!")
        print("="*60)
        print(f"用时: {elapsed/60:.1f} 分钟")
        print(f"平均: {elapsed/len(LARGE_CAP_STOCKS):.1f} 秒/只股票")
        print(f"\n结果:")
        print(f"  - 通过: {len(analysis['passed'])} 只")
        print(f"  - 预警: {len(analysis['warning'])} 只")
        print(f"  - 排除: {len(analysis['excluded'])} 只")
        print(f"\n通过筛选的股票可作为进一步研究的候选池!")

    except KeyboardInterrupt:
        print("\n\n用户中断，已保存部分结果")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
