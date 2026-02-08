# -*- coding: utf-8 -*-
"""
数据下载脚本

首次使用：下载指定股票的历史数据到本地数据库
基于 Baostock 数据源，稳定可靠，支持日线/周线/分钟线/财务数据
"""

import sys

from data_manager import DataManager


def main(auto_confirm=False):
    print("="*70)
    print("股票数据下载工具 (Baostock 数据源)")
    print("="*70)
    print("\n本工具将下载以下数据到本地数据库：")
    print("  - 日线：3年历史数据")
    print("  - 周线：3年历史数据")
    print("  - 60分钟：最近30天")
    print("  - 15分钟：最近15天")
    print("  - 财务数据：最近12期财报")
    print("\n数据源：Baostock (稳定、免费、免登录)")
    print("注意：数据T+1更新，分钟线仅最近1-2个月可用")
    print("数据保存位置：data/stock_data.db")
    print("="*70)

    # 定义要下载的股票列表
    # 默认下载沪深300全部成分股，如需自定义，可修改此处
    from data_manager import BaostockDownloader, DatabaseManager
    db = DatabaseManager()
    downloader = BaostockDownloader(db)
    watchlist = downloader.download_hs300_list()

    if not watchlist:
        print("[错误] 无法获取沪深300成分股列表，使用默认测试列表")
        watchlist = ["600519", "000858", "600809", "000333", "000651"]

    print(f"\n准备下载 {len(watchlist)} 只股票的数据")
    print(f"预计用时：{len(watchlist) * 1.5:.0f} 分钟")

    if auto_confirm:
        print("\n[自动模式] 跳过确认，直接开始下载...")
    else:
        confirm = input("\n确认开始下载? (y/n): ")
        if confirm.lower() != 'y':
            print("已取消")
            return

    # 开始下载
    dm = DataManager()
    dm.full_download(symbols=watchlist)

    # 显示统计
    print("\n" + "="*70)
    print("下载完成！数据库存储统计：")
    print("="*70)

    stats = dm.get_stats()
    for table, count in stats.items():
        print(f"  {table:25s}: {count:8,} 条记录")

    print("\n" + "="*70)
    print("提示：")
    print("  1. 现在可以运行 test_local_db.py 测试分析功能")
    print("  2. 每天收盘后运行 daily_update.py 更新数据")
    print("="*70)


if __name__ == "__main__":
    # 支持命令行参数 -y 或 --auto 来自动确认
    auto = len(sys.argv) > 1 and sys.argv[1] in ('-y', '--auto', '-auto')
    main(auto_confirm=auto)
