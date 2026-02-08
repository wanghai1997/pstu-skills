# -*- coding: utf-8 -*-
"""
沪深300成分股数据下载脚本

下载沪深300指数成分股的历史数据
使用保守模式，避免触发Baostock限流

使用方法:
    python download_hs300.py

参数:
    --conservative  启用保守模式（默认已启用）
    --fast          使用快速模式（不推荐，可能触发限流）
"""

import sys
import argparse

from data_manager import DataManager, BaostockDownloader


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='下载沪深300成分股数据')
    parser.add_argument(
        '--fast', action='store_true',
        help='使用快速模式（不推荐，可能触发限流）'
    )
    args = parser.parse_args()

    use_conservative = not args.fast

    print("="*70)
    print("沪深300成分股数据下载")
    print("="*70)
    print("\n下载范围:")
    print("  - 股票池: 沪深300指数成分股（约300只）")
    print("  - 日线: 3年历史数据")
    print("  - 周线: 3年历史数据")
    print("  - 60分钟: 最近30天")
    print("  - 15分钟: 最近15天")
    print("  - 财务数据: 最近12期财报")
    print("\n数据源: Baostock")
    print("="*70)

    if use_conservative:
        print("\n[保守模式] 已启用")
        print("  - 每次请求间隔: 1秒")
        print("  - 每只股票间隔: 3秒")
        print("  - 每3只股票长暂停: 5秒")
        print("\n预计下载时间: 约 20-30 分钟")
    else:
        print("\n[快速模式] 已启用 - 注意可能触发限流")
        print("\n预计下载时间: 约 10-15 分钟")

    print("\n按 Ctrl+C 可随时中断，已下载的数据会被保存")
    print("="*70)

    # 确认
    try:
        confirm = input("\n确认开始下载? (y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return
    except KeyboardInterrupt:
        print("\n已取消")
        return

    # 初始化
    dm = DataManager()
    downloader = dm.downloader

    # 获取沪深300成分股列表
    symbols = downloader.download_hs300_list()

    if not symbols:
        print("\n[错误] 无法获取沪深300成分股列表")
        return

    print(f"\n获取到 {len(symbols)} 只沪深300成分股")

    # 开始下载
    try:
        dm.full_download(symbols=symbols, use_conservative=use_conservative)
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消下载")
        print("已下载的数据已保存到数据库")
        return

    print("\n" + "="*70)
    print("下载完成!")
    print("="*70)
    print("\n后续操作:")
    print("  1. 运行 python check_db.py 查看数据库统计")
    print("  2. 运行 python verify_data.py 验证数据完整性")
    print("  3. 每天收盘后运行 python daily_update.py 增量更新")
    print("="*70)


if __name__ == "__main__":
    main()
