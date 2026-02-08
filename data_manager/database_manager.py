# -*- coding: utf-8 -*-
"""
本地数据库管理模块

使用SQLite存储多周期股票数据，包括：
- 日线/周线/60分钟/15分钟K线数据
- 财务数据（三大报表）
- 股票基本信息

实现首次全量下载 + 每日增量更新
"""

import sqlite3
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


class DatabaseManager:
    """
    数据库管理器

    管理所有股票数据的存储和查询
    """

    def __init__(self, db_path="data/stock_data.db"):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_dir()
        self._init_tables()

    def _ensure_dir(self):
        """确保数据库目录存在"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def _init_tables(self):
        """初始化数据表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 1. 股票基本信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                industry TEXT,
                market TEXT,
                list_date TEXT,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 2. 日线数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_prices (
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                close REAL,
                high REAL,
                low REAL,
                volume REAL,
                amount REAL,
                PRIMARY KEY (symbol, date),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')

        # 3. 周线数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_prices (
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                close REAL,
                high REAL,
                low REAL,
                volume REAL,
                amount REAL,
                PRIMARY KEY (symbol, date),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')

        # 4. 60分钟数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS min60_prices (
                symbol TEXT NOT NULL,
                datetime TEXT NOT NULL,
                open REAL,
                close REAL,
                high REAL,
                low REAL,
                volume REAL,
                amount REAL,
                PRIMARY KEY (symbol, datetime),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')

        # 5. 15分钟数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS min15_prices (
                symbol TEXT NOT NULL,
                datetime TEXT NOT NULL,
                open REAL,
                close REAL,
                high REAL,
                low REAL,
                volume REAL,
                amount REAL,
                PRIMARY KEY (symbol, datetime),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')

        # 6. 财务摘要表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financial_abstract (
                symbol TEXT NOT NULL,
                report_date TEXT NOT NULL,
                net_profit REAL,
                revenue REAL,
                eps REAL,
                roe REAL,
                gross_margin REAL,
                net_margin REAL,
                debt_ratio REAL,
                cash_flow_portrait TEXT,
                PRIMARY KEY (symbol, report_date),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')

        # 7. 资产负债表 - 支持原始报表和季频偿债能力指标
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS balance_sheet (
                symbol TEXT NOT NULL,
                report_date TEXT NOT NULL,
                -- 原始报表字段
                total_assets REAL,
                total_liabilities REAL,
                equity REAL,
                cash REAL,
                receivables REAL,
                inventory REAL,
                -- 季频偿债能力指标 (Baostock)
                liabilityToAsset REAL,        -- 资产负债率
                currentRatio REAL,            -- 流动比率
                quickRatio REAL,              -- 速动比率
                cashRatio REAL,               -- 现金比率
                YOYLiability REAL,            -- 负债同比
                assetToEquity REAL,           -- 权益乘数
                PRIMARY KEY (symbol, report_date),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')

        # 8. 利润表 - 支持原始报表和季频盈利能力指标
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS income_statement (
                symbol TEXT NOT NULL,
                report_date TEXT NOT NULL,
                -- 原始报表字段
                revenue REAL,
                cost REAL,
                gross_profit REAL,
                operating_profit REAL,
                net_profit REAL,
                sales_expense REAL,
                admin_expense REAL,
                finance_expense REAL,
                -- 季频盈利能力指标 (Baostock)
                roeAvg REAL,                  -- 净资产收益率
                npMargin REAL,                -- 净利率
                gpMargin REAL,                -- 毛利率
                epsTTM REAL,                  -- 每股收益TTM
                MBRevenue REAL,               -- 主营收入
                totalShare REAL,              -- 总股本
                liqaShare REAL,               -- 流通股本
                PRIMARY KEY (symbol, report_date),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')

        # 9. 现金流量表 - 支持原始报表和季频现金流量指标
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cash_flow (
                symbol TEXT NOT NULL,
                report_date TEXT NOT NULL,
                -- 原始报表字段
                operating_cash_flow REAL,
                investing_cash_flow REAL,
                financing_cash_flow REAL,
                net_cash_flow REAL,
                -- 季频现金流量指标 (Baostock)
                cfoToNp REAL,                 -- 经营现金流与净利润比
                cfoToOR REAL,                 -- 经营现金流与营收比
                CFO REAL,                     -- 经营活动现金流净额
                CFI REAL,                     -- 投资活动现金流净额
                CFF REAL,                     -- 筹资活动现金流净额
                PRIMARY KEY (symbol, report_date),
                FOREIGN KEY (symbol) REFERENCES stocks(symbol)
            )
        ''')

        # 10. 更新日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS update_log (
                table_name TEXT PRIMARY KEY,
                last_update DATE,
                record_count INTEGER,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()
        print(f"[数据库] 初始化完成: {self.db_path}")

    # ==================== 查询方法 ====================

    def get_stock_info(self, symbol):
        """获取股票基本信息"""
        conn = self._get_connection()
        df = pd.read_sql_query(
            "SELECT * FROM stocks WHERE symbol = ?",
            conn,
            params=(symbol,)
        )
        conn.close()
        return df.iloc[0].to_dict() if not df.empty else None

    def get_daily_prices(self, symbol, days=250):
        """
        获取日线数据

        Args:
            symbol: 股票代码
            days: 最近N天

        Returns:
            DataFrame: 日线数据
        """
        conn = self._get_connection()

        # 计算起始日期
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        df = pd.read_sql_query(
            """
            SELECT * FROM daily_prices
            WHERE symbol = ? AND date >= ?
            ORDER BY date ASC
            """,
            conn,
            params=(symbol, start_date)
        )
        conn.close()

        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        return df

    def get_weekly_prices(self, symbol, weeks=100):
        """获取周线数据"""
        conn = self._get_connection()

        start_date = (datetime.now() - timedelta(weeks=weeks)).strftime('%Y-%m-%d')

        df = pd.read_sql_query(
            """
            SELECT * FROM weekly_prices
            WHERE symbol = ? AND date >= ?
            ORDER BY date ASC
            """,
            conn,
            params=(symbol, start_date)
        )
        conn.close()

        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        return df

    def get_min60_prices(self, symbol, days=30):
        """获取60分钟数据"""
        conn = self._get_connection()

        start_datetime = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

        df = pd.read_sql_query(
            """
            SELECT * FROM min60_prices
            WHERE symbol = ? AND datetime >= ?
            ORDER BY datetime ASC
            """,
            conn,
            params=(symbol, start_datetime)
        )
        conn.close()

        if not df.empty:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df.set_index('datetime', inplace=True)

        return df

    def get_min15_prices(self, symbol, days=15):
        """获取15分钟数据"""
        conn = self._get_connection()

        start_datetime = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

        df = pd.read_sql_query(
            """
            SELECT * FROM min15_prices
            WHERE symbol = ? AND datetime >= ?
            ORDER BY datetime ASC
            """,
            conn,
            params=(symbol, start_datetime)
        )
        conn.close()

        if not df.empty:
            df['datetime'] = pd.to_datetime(df['datetime'])
            df.set_index('datetime', inplace=True)

        return df

    def get_all_timeframe_data(self, symbol):
        """
        一次性获取所有周期数据

        Returns:
            dict: 各周期数据
        """
        return {
            'daily': self.get_daily_prices(symbol),
            'weekly': self.get_weekly_prices(symbol),
            '60min': self.get_min60_prices(symbol),
            '15min': self.get_min15_prices(symbol),
        }

    def get_financial_data(self, symbol):
        """
        获取财务数据

        Returns:
            dict: 财务数据
        """
        conn = self._get_connection()

        # 获取最新财务摘要
        abstract = pd.read_sql_query(
            "SELECT * FROM financial_abstract WHERE symbol = ? ORDER BY report_date DESC LIMIT 5",
            conn,
            params=(symbol,)
        )

        # 获取最新资产负债表
        balance = pd.read_sql_query(
            "SELECT * FROM balance_sheet WHERE symbol = ? ORDER BY report_date DESC LIMIT 5",
            conn,
            params=(symbol,)
        )

        # 获取最新利润表
        income = pd.read_sql_query(
            "SELECT * FROM income_statement WHERE symbol = ? ORDER BY report_date DESC LIMIT 5",
            conn,
            params=(symbol,)
        )

        # 获取最新现金流量表
        cashflow = pd.read_sql_query(
            "SELECT * FROM cash_flow WHERE symbol = ? ORDER BY report_date DESC LIMIT 5",
            conn,
            params=(symbol,)
        )

        conn.close()

        return {
            'abstract': abstract,
            'balance_sheet': balance,
            'income_statement': income,
            'cash_flow': cashflow,
        }

    def get_last_update(self, table_name):
        """获取某表的最后更新时间"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT last_update FROM update_log WHERE table_name = ?",
            (table_name,)
        )
        result = cursor.fetchone()
        conn.close()

        return result[0] if result else None

    # ==================== 插入/更新方法 ====================

    def save_stock_list(self, stocks_df):
        """保存股票列表"""
        conn = self._get_connection()
        stocks_df.to_sql('stocks', conn, if_exists='replace', index=False)

        # 更新日志
        self._update_log(conn, 'stocks', len(stocks_df))

        conn.close()
        print(f"[数据库] 保存股票列表: {len(stocks_df)} 只")

    def save_daily_prices(self, symbol, df):
        """保存日线数据"""
        if df is None or df.empty:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        # 先删除该股票的旧数据（避免主键冲突）
        cursor.execute("DELETE FROM daily_prices WHERE symbol = ?", (symbol,))
        conn.commit()

        # 添加symbol列
        df_copy = df.copy()
        df_copy['symbol'] = symbol

        # 确保列名正确
        if 'date' in df_copy.columns:
            df_copy = df_copy.reset_index() if df_copy.index.name == 'date' else df_copy

        # 保存新数据
        df_copy.to_sql('daily_prices', conn, if_exists='append', index=False)

        self._update_log(conn, 'daily_prices', len(df_copy), symbol)
        conn.commit()
        conn.close()

    def save_weekly_prices(self, symbol, df):
        """保存周线数据"""
        if df is None or df.empty:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        # 先删除该股票的旧数据（避免主键冲突）
        cursor.execute("DELETE FROM weekly_prices WHERE symbol = ?", (symbol,))
        conn.commit()

        df_copy = df.copy()
        df_copy['symbol'] = symbol

        if 'date' in df_copy.columns:
            df_copy = df_copy.reset_index() if df_copy.index.name == 'date' else df_copy

        df_copy.to_sql('weekly_prices', conn, if_exists='append', index=False)

        self._update_log(conn, 'weekly_prices', len(df_copy), symbol)
        conn.commit()
        conn.close()

    def save_min60_prices(self, symbol, df):
        """保存60分钟数据"""
        if df is None or df.empty:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        # 先删除该股票的旧数据（避免主键冲突）
        cursor.execute("DELETE FROM min60_prices WHERE symbol = ?", (symbol,))
        conn.commit()

        df_copy = df.copy()
        df_copy['symbol'] = symbol

        if 'datetime' in df_copy.columns:
            df_copy = df_copy.reset_index() if df_copy.index.name == 'datetime' else df_copy

        df_copy.to_sql('min60_prices', conn, if_exists='append', index=False)

        self._update_log(conn, 'min60_prices', len(df_copy), symbol)
        conn.commit()
        conn.close()

    def save_min15_prices(self, symbol, df):
        """保存15分钟数据"""
        if df is None or df.empty:
            return

        conn = self._get_connection()
        cursor = conn.cursor()

        # 先删除该股票的旧数据（避免主键冲突）
        cursor.execute("DELETE FROM min15_prices WHERE symbol = ?", (symbol,))
        conn.commit()

        df_copy = df.copy()
        df_copy['symbol'] = symbol

        if 'datetime' in df_copy.columns:
            df_copy = df_copy.reset_index() if df_copy.index.name == 'datetime' else df_copy

        df_copy.to_sql('min15_prices', conn, if_exists='append', index=False)

        self._update_log(conn, 'min15_prices', len(df_copy), symbol)
        conn.commit()
        conn.close()

    def save_financial_data(self, symbol, abstract_df, balance_df, income_df, cashflow_df):
        """保存财务数据"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 保存财务摘要表
        if abstract_df is not None and not abstract_df.empty:
            # 添加symbol列
            abstract_save = abstract_df.copy()
            abstract_save['symbol'] = symbol
            # 去重：保留每个report_date的第一条记录
            abstract_save = abstract_save.drop_duplicates(subset=['symbol', 'report_date'], keep='first')
            # 先删除该股票的旧数据
            cursor.execute("DELETE FROM financial_abstract WHERE symbol = ?", (symbol,))
            conn.commit()
            # 插入新数据
            abstract_save.to_sql('financial_abstract', conn, if_exists='append', index=False)

        # 保存季频偿债能力数据 (balance_df)
        if balance_df is not None and not balance_df.empty:
            # 重命名列以匹配数据库表结构
            balance_save = balance_df.copy()
            balance_save['symbol'] = symbol
            if 'pubDate' in balance_save.columns:
                balance_save['report_date'] = balance_save['pubDate']
            # 去重
            balance_save = balance_save.drop_duplicates(subset=['symbol', 'report_date'], keep='first')
            # 先删除旧数据
            cursor.execute("DELETE FROM balance_sheet WHERE symbol = ?", (symbol,))
            conn.commit()
            # 确保列名匹配
            db_columns = ['symbol', 'report_date', 'liabilityToAsset', 'currentRatio',
                         'quickRatio', 'cashRatio', 'YOYLiability', 'assetToEquity']
            available_cols = [c for c in db_columns if c in balance_save.columns]
            if available_cols:
                balance_save[available_cols].to_sql('balance_sheet', conn, if_exists='append', index=False)

        # 保存季频盈利能力数据 (income_df)
        if income_df is not None and not income_df.empty:
            # 重命名列以匹配数据库表结构
            income_save = income_df.copy()
            income_save['symbol'] = symbol
            if 'pubDate' in income_save.columns:
                income_save['report_date'] = income_save['pubDate']
            # 去重
            income_save = income_save.drop_duplicates(subset=['symbol', 'report_date'], keep='first')
            # 先删除旧数据
            cursor.execute("DELETE FROM income_statement WHERE symbol = ?", (symbol,))
            conn.commit()
            # 确保列名匹配
            db_columns = ['symbol', 'report_date', 'roeAvg', 'npMargin', 'gpMargin',
                         'epsTTM', 'MBRevenue', 'totalShare', 'liqaShare']
            available_cols = [c for c in db_columns if c in income_save.columns]
            if available_cols:
                income_save[available_cols].to_sql('income_statement', conn, if_exists='append', index=False)

        # 保存季频现金流量数据 (cashflow_df)
        if cashflow_df is not None and not cashflow_df.empty:
            # 重命名列以匹配数据库表结构
            cash_save = cashflow_df.copy()
            cash_save['symbol'] = symbol
            if 'pubDate' in cash_save.columns:
                cash_save['report_date'] = cash_save['pubDate']
            # 去重
            cash_save = cash_save.drop_duplicates(subset=['symbol', 'report_date'], keep='first')
            # 先删除旧数据
            cursor.execute("DELETE FROM cash_flow WHERE symbol = ?", (symbol,))
            conn.commit()
            # 确保列名匹配
            db_columns = ['symbol', 'report_date', 'cfoToNp', 'cfoToOR', 'CFO', 'CFI', 'CFF']
            available_cols = [c for c in db_columns if c in cash_save.columns]
            if available_cols:
                cash_save[available_cols].to_sql('cash_flow', conn, if_exists='append', index=False)

        self._update_log(conn, 'financial', len(abstract_df) if abstract_df is not None else 0, symbol)
        conn.commit()
        conn.close()

    def _update_log(self, conn, table_name, count=None, symbol=None):
        """更新日志"""
        cursor = conn.cursor()

        today = datetime.now().strftime('%Y-%m-%d')

        cursor.execute("""
            INSERT OR REPLACE INTO update_log (table_name, last_update, record_count, update_time)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """, (table_name, today, count))

    # ==================== 工具方法 ====================

    def check_data_exists(self, symbol, table='daily_prices'):
        """检查某股票数据是否存在"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"SELECT COUNT(*) FROM {table} WHERE symbol = ?",
            (symbol,)
        )
        count = cursor.fetchone()[0]
        conn.close()

        return count > 0

    def get_data_stats(self):
        """获取数据统计信息"""
        conn = self._get_connection()
        cursor = conn.cursor()

        stats = {}

        tables = [
            'stocks', 'daily_prices', 'weekly_prices',
            'min60_prices', 'min15_prices',
            'financial_abstract', 'balance_sheet',
            'income_statement', 'cash_flow'
        ]

        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except:
                stats[table] = 0

        conn.close()
        return stats

    def get_symbols_with_data(self):
        """获取有日线数据的所有股票代码"""
        conn = self._get_connection()
        df = pd.read_sql_query(
            "SELECT DISTINCT symbol FROM daily_prices",
            conn
        )
        conn.close()
        return df['symbol'].tolist()

    def get_symbols_with_financial_data(self):
        """获取有财务数据的所有股票代码"""
        conn = self._get_connection()
        try:
            df = pd.read_sql_query(
                "SELECT DISTINCT symbol FROM financial_abstract",
                conn
            )
            return df['symbol'].tolist()
        except Exception:
            return []
        finally:
            conn.close()
