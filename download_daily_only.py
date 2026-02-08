# -*- coding: utf-8 -*-
"""
只下载日线数据（用于补全缺失的日线）

使用方法:
    python download_daily_only.py          # 下载所有股票的日线
    python download_daily_only.py -y       # 自动确认
"""

import sys
from data_manager import BaostockDownloader, DatabaseManager


def main(auto_confirm=False):
    print("="*70)
    print("日线数据补下载工具")
    print("="*70)
    print("\n本工具仅下载日线数据（5年历史），不下载其他类型")
    print("适用于：日线数据缺失或需要重新下载的情况")
    print("="*70)

    # 获取股票列表
    db = DatabaseManager()
    downloader = BaostockDownloader(db)
    watchlist = downloader.download_hs300_list()

    if not watchlist:
        print("[错误] 无法获取沪深300成分股列表")
        return

    print(f"\n准备下载 {len(watchlist)} 只股票的日线数据")
    print(f"预计用时：{len(watchlist) * 0.3:.0f} 分钟")

    if auto_confirm:
        print("\n[自动模式] 跳过确认，直接开始下载...")
    else:
        confirm = input("\n确认开始下载? (y/n): ")
        if confirm.lower() != 'y':
            print("已取消")
            return

    # 只下载日线数据
    success_count = 0
    failed_stocks = []

    for i, symbol in enumerate(watchlist, 1):
        print(f"\n[{i}/{len(watchlist)}] {symbol}")
        print("-" * 40)

        try:
            # 只下载日线，years=5
            if downloader.download_daily_prices(symbol, years=5):
                success_count += 1
            else:
                failed_stocks.append(symbol)
        except Exception as e:
            print(f"  [错误] {e}")
            failed_stocks.append(symbol)

    # 显示结果
    print("\n" + "="*70)
    print("下载完成")
    print("="*70)
    print(f"成功: {success_count}/{len(watchlist)}")

    if failed_stocks:
        print(f"失败: {len(failed_stocks)} 只")
        print(f"股票: {', '.join(failed_stocks[:10])}")

    print("\n验证数据完整性:")
    print("  python data_quality_monitor.py")
    print("="*70)


if __name__ == "__main__":
    auto = len(sys.argv) > 1 and sys.argv[1] in ('-y', '--auto', '-auto')
    main(auto_confirm=auto)
