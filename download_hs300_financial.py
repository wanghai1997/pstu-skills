# -*- coding: utf-8 -*-
"""
下载沪深300成分股的财务数据

使用方法:
    python download_hs300_financial.py
"""

import sys
import time

sys.path.insert(0, '.')

from data_manager import DatabaseManager, BaostockDownloader


def download_hs300_financial():
    """下载沪深300所有成分股的财务数据"""
    print("=" * 70)
    print("下载沪深300成分股财务数据")
    print("=" * 70)

    # 初始化
    db = DatabaseManager()
    downloader = BaostockDownloader(db)

    # 1. 获取沪深300成分股列表
    print("\n步骤1: 获取沪深300成分股列表...")
    symbols = downloader.download_hs300_list()

    if not symbols:
        print("[错误] 无法获取沪深300成分股列表")
        return

    print(f"\n沪深300共有 {len(symbols)} 只成分股")

    # 2. 检查哪些股票已经有财务数据
    existing = db.get_symbols_with_data()
    print(f"数据库中已有 {len(existing)} 只股票有财务数据")

    # 3. 筛选需要下载的股票
    to_download = [s for s in symbols if s not in existing]
    already_have = [s for s in symbols if s in existing]

    print(f"已有数据: {len(already_have)} 只")
    print(f"需要下载: {len(to_download)} 只")

    if not to_download:
        print("\n[OK] 所有沪深300股票财务数据已存在，无需下载")
        return

    # 4. 批量下载财务数据
    print(f"\n步骤2: 开始下载 {len(to_download)} 只股票的财务数据...")
    print("=" * 70)

    success = 0
    failed = 0
    failed_list = []

    for i, symbol in enumerate(to_download, 1):
        print(f"\n[{i}/{len(to_download)}] 下载 {symbol}...")
        try:
            result = downloader.download_financial_data(symbol)
            if result:
                success += 1
            else:
                failed += 1
                failed_list.append(symbol)
            # 每次下载后休息，避免请求过快
            time.sleep(0.5)
        except Exception as e:
            print(f"  [错误] {symbol}: {e}")
            failed += 1
            failed_list.append(symbol)
            time.sleep(1)

    # 5. 汇总结果
    print("\n" + "=" * 70)
    print("下载完成")
    print("=" * 70)
    print(f"总计: {len(to_download)} 只")
    print(f"  成功: {success} 只")
    print(f"  失败: {failed} 只")

    if failed_list:
        print(f"\n失败列表: {', '.join(failed_list[:10])}")
        if len(failed_list) > 10:
            print(f"... 等共 {len(failed_list)} 只")

    # 6. 验证数据
    print("\n步骤3: 验证数据...")
    updated = db.get_symbols_with_data()
    hs300_with_data = [s for s in symbols if s in updated]
    print(f"沪深300股票中已有财务数据: {len(hs300_with_data)}/{len(symbols)} 只")

    print("\n[OK] 完成！")


if __name__ == "__main__":
    try:
        download_hs300_financial()
    except KeyboardInterrupt:
        print("\n\n[中断] 用户取消下载")
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
