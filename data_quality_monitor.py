# -*- coding: utf-8 -*-
"""
数据质量监控脚本

功能：
1. 检查各表数据完整性
2. 检查数据时间范围
3. 检测缺失数据的股票
4. 生成补下载清单

使用方法:
    python data_quality_monitor.py              # 完整检查
    python data_quality_monitor.py --fix        # 自动修复（下载缺失数据）
    python data_quality_monitor.py --stock 600519  # 检查单只股票
"""

import sys
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, '.')
from data_manager import DatabaseManager


class DataQualityMonitor:
    """数据质量监控器"""

    def __init__(self, db_path='data/stock_data.db'):
        self.db_path = db_path
        self.issues = []  # 存储发现的问题

    def _connect(self):
        """连接数据库"""
        return sqlite3.connect(self.db_path)

    def check_all(self):
        """执行所有检查"""
        print("=" * 70)
        print("数据质量监控报告")
        print("=" * 70)
        print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"数据库: {self.db_path}")
        print("=" * 70)

        # 1. 检查基本信息
        self._check_basic_stats()

        # 2. 检查日线数据质量
        self._check_price_data_quality('daily_prices', '日线', 5)

        # 3. 检查周线数据质量
        self._check_price_data_quality('weekly_prices', '周线', 5)

        # 4. 检查60分钟数据质量
        self._check_price_data_quality('min60_prices', '60分钟', 4)

        # 5. 检查15分钟数据质量
        self._check_price_data_quality('min15_prices', '15分钟', 2)

        # 6. 检查财务数据质量
        self._check_financial_data_quality()

        # 7. 生成汇总报告
        self._print_summary()

    def _check_basic_stats(self):
        """检查基本统计信息"""
        print("\n【1. 数据库概况】")

        conn = self._connect()
        cursor = conn.cursor()

        # 获取所有表的数据量
        tables = [
            'stocks', 'daily_prices', 'weekly_prices',
            'min60_prices', 'min15_prices',
            'financial_abstract', 'balance_sheet',
            'income_statement', 'cash_flow'
        ]

        stats = {}
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            except:
                stats[table] = 0

        conn.close()

        # 打印统计
        for table, count in stats.items():
            print(f"  {table:25s}: {count:>10,} 条")

        # 检查是否有股票列表
        if stats.get('stocks', 0) == 0:
            self.issues.append({
                'type': '严重',
                'message': '股票列表为空，请先运行 download_data.py'
            })

    def _check_price_data_quality(self, table, name, expected_years):
        """
        检查价格数据质量

        Args:
            table: 表名
            name: 数据类型名称
            expected_years: 期望的数据年数
        """
        print(f"\n【{name}数据检查】")

        conn = self._connect()

        # 获取股票列表
        stocks_df = pd.read_sql("SELECT symbol FROM stocks", conn)
        if stocks_df.empty:
            print(f"  [警告] 没有股票列表")
            conn.close()
            return

        all_symbols = set(stocks_df['symbol'].tolist())

        # 检查有数据的股票（分钟数据用datetime列，日线/周线用date列）
        if 'min' in table:
            df = pd.read_sql(f"SELECT symbol, COUNT(*) as count, MIN(datetime) as min_date, MAX(datetime) as max_date FROM {table} GROUP BY symbol", conn)
        else:
            df = pd.read_sql(f"SELECT symbol, COUNT(*) as count, MIN(date) as min_date, MAX(date) as max_date FROM {table} GROUP BY symbol", conn)
        conn.close()

        if df.empty:
            self.issues.append({
                'type': '严重',
                'message': f'{name}数据表为空'
            })
            print(f"  [错误] {name}数据表为空")
            return

        # 统计
        symbols_with_data = set(df['symbol'].tolist())
        missing_symbols = all_symbols - symbols_with_data

        print(f"  有数据的股票: {len(symbols_with_data)}/{len(all_symbols)}")
        print(f"  缺失数据的股票: {len(missing_symbols)}")

        # 检查数据条数（粗略估计：一年约250个交易日）
        expected_records = expected_years * 250

        low_count_stocks = df[df['count'] < expected_records * 0.5]  # 少于50%认为数据不足
        if len(low_count_stocks) > 0:
            print(f"  数据不足的股票: {len(low_count_stocks)} 只")
            self.issues.append({
                'type': '警告',
                'message': f'{name}数据：{len(low_count_stocks)} 只股票数据不足（少于{expected_records * 0.5:.0f}条）',
                'details': low_count_stocks['symbol'].tolist()[:10]  # 只记录前10个
            })

        # 检查最新数据日期
        df['max_date'] = pd.to_datetime(df['max_date'])
        latest_date = df['max_date'].max()
        print(f"  最新数据日期: {latest_date.strftime('%Y-%m-%d')}")

        # 如果最新数据超过5天前，提醒更新
        if (datetime.now() - latest_date).days > 5:
            self.issues.append({
                'type': '提醒',
                'message': f'{name}数据可能需要更新，最新数据为 {latest_date.strftime("%Y-%m-%d")}'
            })

        # 记录缺失的股票
        if missing_symbols:
            self.issues.append({
                'type': '警告',
                'message': f'{name}数据：{len(missing_symbols)} 只股票缺失数据',
                'details': list(missing_symbols)[:10]
            })

        return list(missing_symbols)

    def _check_financial_data_quality(self):
        """检查财务数据质量"""
        print("\n【财务数据检查】")

        conn = self._connect()

        # 检查财务摘要表
        for table, name in [
            ('financial_abstract', '财务摘要'),
            ('balance_sheet', '资产负债表'),
            ('income_statement', '利润表'),
            ('cash_flow', '现金流量表')
        ]:
            df = pd.read_sql(f"SELECT symbol, COUNT(*) as count FROM {table} GROUP BY symbol", conn)

            if df.empty:
                print(f"  [错误] {name}表为空")
                self.issues.append({
                    'type': '严重',
                    'message': f'{name}表为空'
                })
                continue

            # 统计每只股票的财报期数
            avg_records = df['count'].mean()
            print(f"  {name}: 平均 {avg_records:.1f} 期/股票")

            # 少于4期的认为数据不足
            low_count = df[df['count'] < 4]
            if len(low_count) > 0:
                self.issues.append({
                    'type': '警告',
                    'message': f'{name}：{len(low_count)} 只股票财报数据不足（少于4期）'
                })

        conn.close()

    def _print_summary(self):
        """打印汇总报告"""
        print("\n" + "=" * 70)
        print("数据质量汇总")
        print("=" * 70)

        if not self.issues:
            print("[OK] 所有检查通过，数据质量良好！")
            return

        # 按类型分组
        severe = [i for i in self.issues if i['type'] == '严重']
        warnings = [i for i in self.issues if i['type'] == '警告']
        reminders = [i for i in self.issues if i['type'] == '提醒']

        if severe:
            print(f"\n[严重] 问题 ({len(severe)}项):")
            for issue in severe:
                print(f"   - {issue['message']}")

        if warnings:
            print(f"\n[警告] ({len(warnings)}项):")
            for issue in warnings:
                print(f"   - {issue['message']}")
                if 'details' in issue:
                    print(f"     涉及: {', '.join(issue['details'][:5])}")

        if reminders:
            print(f"\n[提醒] ({len(reminders)}项):")
            for issue in reminders:
                print(f"   - {issue['message']}")

        print("\n" + "=" * 70)
        print("建议操作:")
        print("  1. 运行 python data_quality_monitor.py --fix 自动修复")
        print("  2. 或运行 python download_data.py 重新下载数据")
        print("=" * 70)

    def generate_fix_script(self):
        """生成修复脚本（下载缺失数据）"""
        print("\n正在生成修复方案...")

        # 收集所有缺失数据的股票
        missing_daily = self._get_missing_symbols('daily_prices')
        missing_weekly = self._get_missing_symbols('weekly_prices')

        if not missing_daily and not missing_weekly:
            print("[OK] 没有缺失数据，无需修复")
            return

        # 生成补下载脚本
        all_missing = set(missing_daily + missing_weekly)
        print(f"\n发现 {len(all_missing)} 只股票需要补下载数据")
        print(f"股票列表: {', '.join(list(all_missing)[:10])}{'...' if len(all_missing) > 10 else ''}")

        # 这里可以调用下载器进行补下载
        print("\n执行补下载...")
        self._download_missing(list(all_missing))

    def _get_missing_symbols(self, table):
        """获取缺失数据的股票代码"""
        conn = self._connect()

        # 获取所有股票
        stocks_df = pd.read_sql("SELECT symbol FROM stocks", conn)
        if stocks_df.empty:
            conn.close()
            return []

        all_symbols = set(stocks_df['symbol'].tolist())

        # 获取有数据的股票
        df = pd.read_sql(f"SELECT DISTINCT symbol FROM {table}", conn)
        conn.close()

        if df.empty:
            return list(all_symbols)

        symbols_with_data = set(df['symbol'].tolist())
        return list(all_symbols - symbols_with_data)

    def _download_missing(self, symbols):
        """下载缺失数据"""
        if not symbols:
            return

        try:
            from data_manager import BaostockDownloader, DatabaseManager

            db = DatabaseManager()
            downloader = BaostockDownloader(db)

            print(f"\n开始补下载 {len(symbols)} 只股票的数据...")

            for i, symbol in enumerate(symbols, 1):
                print(f"\n[{i}/{len(symbols)}] 补下载 {symbol}...")
                try:
                    downloader.full_download(symbol)
                except Exception as e:
                    print(f"  [错误] {symbol} 下载失败: {e}")

            print(f"\n[OK] 补下载完成")

        except Exception as e:
            print(f"[错误] 补下载失败: {e}")
            print("建议手动运行: python download_data.py")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='数据质量监控')
    parser.add_argument('--fix', action='store_true', help='自动修复缺失数据')
    parser.add_argument('--stock', type=str, help='检查特定股票')

    args = parser.parse_args()

    monitor = DataQualityMonitor()

    if args.stock:
        # 检查单只股票
        print(f"检查股票: {args.stock}")
        # TODO: 实现单只股票检查
    else:
        # 完整检查
        monitor.check_all()

        if args.fix:
            monitor.generate_fix_script()


if __name__ == "__main__":
    main()
