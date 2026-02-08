# -*- coding: utf-8 -*-
"""
数据管理模块

管理本地股票数据库，支持多周期数据存储
基于 Baostock 数据源，支持日线/周线/分钟线/财务数据

使用示例:
    from data_manager import DataManager

    # 初始化
    dm = DataManager()

    # 首次下载（3年历史数据）
    dm.full_download(symbols=["600519", "000858"])

    # 每日更新
    dm.daily_update()

    # 获取数据用于分析
    daily = dm.get_daily_prices("600519")
    weekly = dm.get_weekly_prices("600519")
    min60 = dm.get_min60_prices("600519")
    min15 = dm.get_min15_prices("600519")
"""

from .database_manager import DatabaseManager
from .baostock_downloader import BaostockDownloader


class DataManager:
    """
    数据管理器（便捷接口）

    整合数据库管理和数据下载功能
    使用 Baostock 作为主数据源
    """

    def __init__(self, db_path="data/stock_data.db"):
        self.db = DatabaseManager(db_path)
        self.downloader = BaostockDownloader(self.db)

    # ========== 下载方法 ==========

    def full_download(self, symbols=None, max_stocks=None, use_conservative=False):
        """首次全量下载"""
        return self.downloader.full_download(symbols, max_stocks, use_conservative)

    def daily_update(self, delay=1.5):
        """
        每日增量更新

        参数:
            delay: 请求间隔时间(秒)，默认1.5秒，避免服务器压力过大
        """
        return self.downloader.incremental_update(delay=delay)

    def download_stock(self, symbol):
        """下载单只股票的所有数据"""
        print(f"\n下载 {symbol} 的数据...")
        self.downloader.download_daily_prices(symbol, years=3)
        self.downloader.download_weekly_prices(symbol, years=3)
        self.downloader.download_min60_prices(symbol, days=30)
        self.downloader.download_min15_prices(symbol, days=15)
        self.downloader.download_financial_data(symbol)
        print(f"✓ {symbol} 下载完成")

    # ========== 查询方法 ==========

    def get_daily_prices(self, symbol, days=250):
        """获取日线数据"""
        return self.db.get_daily_prices(symbol, days)

    def get_weekly_prices(self, symbol, weeks=100):
        """获取周线数据"""
        return self.db.get_weekly_prices(symbol, weeks)

    def get_min60_prices(self, symbol, days=30):
        """获取60分钟数据"""
        return self.db.get_min60_prices(symbol, days)

    def get_min15_prices(self, symbol, days=15):
        """获取15分钟数据"""
        return self.db.get_min15_prices(symbol, days)

    def get_all_timeframe_data(self, symbol):
        """获取所有周期数据"""
        return self.db.get_all_timeframe_data(symbol)

    def get_financial_data(self, symbol):
        """获取财务数据"""
        return self.db.get_financial_data(symbol)

    # ========== 工具方法 ==========

    def check_data_exists(self, symbol):
        """检查股票数据是否存在"""
        return self.db.check_data_exists(symbol)

    def get_stats(self):
        """获取数据统计"""
        return self.db.get_data_stats()

    def get_symbols(self):
        """获取有数据的股票列表"""
        return self.db.get_symbols_with_data()


__all__ = ['DataManager', 'DatabaseManager', 'BaostockDownloader']
