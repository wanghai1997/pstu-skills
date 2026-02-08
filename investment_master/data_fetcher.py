# -*- coding: utf-8 -*-
"""
多周期数据获取模块

从本地数据库获取股票的多周期K线数据（周线、日线、60分钟、15分钟）
基于 Baostock 数据源，纯本地数据库模式
"""

import pandas as pd

from .config import MULTI_TIMEFRAME_CONFIG


class MultiTimeframeDataFetcher:
    """
    多周期数据获取器

    从本地数据库获取股票在不同时间周期的K线数据
    纯本地数据库模式，无需网络连接
    """

    def __init__(self, db_manager=None):
        """
        初始化数据获取器

        Args:
            db_manager: 数据库管理器实例，为None时自动创建
        """
        self.config = MULTI_TIMEFRAME_CONFIG
        self.data_cache = {}

        # 初始化数据库管理器
        if db_manager is None:
            from data_manager import DatabaseManager
            self.db_manager = DatabaseManager()
        else:
            self.db_manager = db_manager

        print("[数据获取器] 使用本地数据库模式")

    def _get_period_days(self, period):
        """获取数据获取天数"""
        return self.config["data_days"].get(period, 250)

    def fetch_daily_data(self, symbol, days=250):
        """
        获取日线数据

        Args:
            symbol: 股票代码
            days: 获取天数

        Returns:
            DataFrame: 日线数据（包含开盘、收盘、最高、最低、成交量）
        """
        try:
            df = self.db_manager.get_daily_prices(symbol, days)
            if df is not None and not df.empty:
                return df
            else:
                print(f"  [警告] {symbol} 无日线数据，请先运行 download_data.py 下载")
                return None
        except Exception as e:
            print(f"  [错误] 读取日线数据失败 {symbol}: {e}")
            return None

    def fetch_weekly_data(self, symbol, weeks=100):
        """
        获取周线数据

        Args:
            symbol: 股票代码
            weeks: 获取周数

        Returns:
            DataFrame: 周线数据
        """
        try:
            df = self.db_manager.get_weekly_prices(symbol, weeks)
            if df is not None and not df.empty:
                return df
            else:
                print(f"  [警告] {symbol} 无周线数据，请先运行 download_data.py 下载")
                return None
        except Exception as e:
            print(f"  [错误] 读取周线数据失败 {symbol}: {e}")
            return None

    def fetch_intraday_data(self, symbol, period="60"):
        """
        获取分钟级数据

        Args:
            symbol: 股票代码
            period: 分钟周期（"15", "60"）

        Returns:
            DataFrame: 分钟级数据
        """
        try:
            if period == "60":
                df = self.db_manager.get_min60_prices(symbol, days=30)
            elif period == "15":
                df = self.db_manager.get_min15_prices(symbol, days=15)
            else:
                print(f"  [错误] 不支持的周期: {period}")
                return None

            if df is not None and not df.empty:
                return df
            else:
                print(f"  [警告] {symbol} 无{period}分钟数据，请先运行 download_data.py 下载")
                return None
        except Exception as e:
            print(f"  [错误] 读取{period}分钟数据失败 {symbol}: {e}")
            return None

    def fetch_all_timeframes(self, symbol):
        """
        一次性获取所有周期的数据

        Args:
            symbol: 股票代码

        Returns:
            dict: 各周期数据字典
        """
        print(f"\n获取 {symbol} 的多周期数据...")
        print("  [模式] 本地数据库")

        result = {
            'symbol': symbol,
            'weekly': None,
            'daily': None,
            '60min': None,
            '15min': None,
        }

        # 获取日线（最基础的数据）
        print("  [获取] 日线数据...")
        result['daily'] = self.fetch_daily_data(symbol)

        # 获取周线
        print("  [获取] 周线数据...")
        result['weekly'] = self.fetch_weekly_data(symbol)

        # 获取60分钟
        print("  [获取] 60分钟数据...")
        result['60min'] = self.fetch_intraday_data(symbol, "60")

        # 获取15分钟
        print("  [获取] 15分钟数据...")
        result['15min'] = self.fetch_intraday_data(symbol, "15")

        # 统计获取结果
        success_count = sum(1 for v in result.values() if v is not None and isinstance(v, pd.DataFrame))
        print(f"  [完成] 成功获取 {success_count}/4 个周期数据")

        return result

    def get_latest_price(self, symbol):
        """
        获取最新股价

        Args:
            symbol: 股票代码

        Returns:
            float: 最新价格
        """
        try:
            df = self.db_manager.get_daily_prices(symbol, days=1)
            if df is not None and not df.empty:
                return float(df.iloc[-1]['close'])
            return None
        except:
            return None

    def get_stock_name(self, symbol):
        """
        获取股票名称

        Args:
            symbol: 股票代码

        Returns:
            str: 股票名称
        """
        try:
            info = self.db_manager.get_stock_info(symbol)
            if info:
                return info.get('name', symbol)
        except:
            pass
        return symbol
