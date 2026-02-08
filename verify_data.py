# -*- coding: utf-8 -*-
"""
验证下载的数据是否可用
"""

from data_manager import DatabaseManager
import pandas as pd

db = DatabaseManager()

print("="*60)
print("验证数据可用性")
print("="*60)

# 测试几只股票
test_symbols = ["600519", "000858", "300750"]

for symbol in test_symbols:
    print(f"\n【{symbol}】")

    # 日线
    daily = db.get_daily_prices(symbol, days=5)
    if daily is not None and not daily.empty:
        print(f"  日线: {len(daily)} 条")
        print(f"    列名: {list(daily.columns)}")
        print(f"    最新数据:\n{daily.tail(1)}")
    else:
        print(f"  日线: 无数据")

    # 周线
    weekly = db.get_weekly_prices(symbol, weeks=3)
    if weekly is not None and not weekly.empty:
        print(f"  周线: {len(weekly)} 条")
    else:
        print(f"  周线: 无数据")

    # 60分钟
    min60 = db.get_min60_prices(symbol, days=3)
    if min60 is not None and not min60.empty:
        print(f"  60分钟: {len(min60)} 条")
    else:
        print(f"  60分钟: 无数据")

    # 15分钟
    min15 = db.get_min15_prices(symbol, days=2)
    if min15 is not None and not min15.empty:
        print(f"  15分钟: {len(min15)} 条")
    else:
        print(f"  15分钟: 无数据")

print("\n" + "="*60)
print("数据验证完成")
print("="*60)
