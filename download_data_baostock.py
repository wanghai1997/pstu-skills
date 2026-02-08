# -*- coding: utf-8 -*-
"""
Baostock 数据下载脚本

使用 Baostock 作为备用数据源下载股票数据
优点：稳定、免费、不需要登录
缺点：数据T+1更新，不支持分钟级数据
"""

import sys

from data_manager.baostock_downloader import BaostockDownloader


def main(auto_confirm=False):
    print("="*70)
    print("Baostock 股票数据下载工具")
    print("="*70)
    print("\n本工具将下载以下数据到本地数据库：")
    print("  - 日线：历史数据（前复权）")
    print("  - 周线：历史数据")
    print("  - 财务数据：最近10期财报")
    print("\n注意：Baostock 数据为T+1更新，不支持分钟级数据")
    print("数据保存位置：data/stock_data.db")
    print("="*70)

    # 定义要下载的股票列表
    watchlist = [
        # 白酒
        "600519",  # 贵州茅台
        "000858",  # 五粮液
        "600809",  # 山西汾酒

        # 消费
        "000333",  # 美的集团
        "000651",  # 格力电器
        "600887",  # 伊利股份
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

        # 其他
        "601899",  # 紫金矿业
        "600900",  # 长江电力
    ]

    print(f"\n准备下载 {len(watchlist)} 只股票的数据")
    print(f"预计用时：约 {len(watchlist) * 0.5:.0f} 分钟")

    if auto_confirm:
        print("\n[自动模式] 跳过确认，直接开始下载...")
    else:
        confirm = input("\n确认开始下载? (y/n): ")
        if confirm.lower() != 'y':
            print("已取消")
            return

    # 开始下载
    downloader = BaostockDownloader()
    downloader.full_download(symbols=watchlist)

    print("\n" + "="*70)
    print("提示：")
    print("  1. 现在可以运行 test_local_db.py 测试分析功能")
    print("  2. 每天收盘后运行 daily_update_baostock.py 更新数据")
    print("  3. Baostock 数据为T+1，当日数据需次日更新")
    print("="*70)


if __name__ == "__main__":
    # 支持命令行参数 -y 或 --auto 来自动确认
    auto = len(sys.argv) > 1 and sys.argv[1] in ('-y', '--auto', '-auto')
    main(auto_confirm=auto)
