# -*- coding: utf-8 -*-
"""
每日数据更新脚本

收盘后运行，增量更新本地数据库
基于 Baostock 数据源（T+1更新）
"""

from data_manager import DataManager
from datetime import datetime


def main():
    print("="*70)
    print("每日数据更新")
    print("="*70)
    print(f"\n当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    dm = DataManager()

    # 检查当前数据状态
    print("\n当前数据库状态:")
    stats = dm.get_stats()
    print(f"  股票数量: {stats.get('stocks', 0)} 只")
    print(f"  日线数据: {stats.get('daily_prices', 0):,} 条")
    print(f"  最后更新: {dm.db.get_last_update('daily_prices') or '未记录'}")

    # 执行更新
    print("\n开始检查更新...")
    updated = dm.daily_update()

    if updated > 0:
        print(f"\n✓ 更新成功: {updated} 只股票")
    else:
        print("\n○ 无需更新（数据已是最新）")

    print("\n" + "="*70)
    print("更新完成！")
    print("="*70)


if __name__ == "__main__":
    main()
