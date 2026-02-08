# -*- coding: utf-8 -*-
"""
检查数据库状态
"""

from data_manager import DatabaseManager

db = DatabaseManager()
stats = db.get_data_stats()

print("="*60)
print("数据库当前状态")
print("="*60)

for table, count in stats.items():
    print(f"  {table:25s}: {count:8,} 条")

print("="*60)

# 检查股票列表
symbols = db.get_symbols_with_data()
print(f"\n有数据的股票数量: {len(symbols)}")
if symbols:
    print(f"前10只股票: {symbols[:10]}")
