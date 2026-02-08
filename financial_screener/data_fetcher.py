# -*- coding: utf-8 -*-
"""
数据获取模块

从本地数据库获取A股财务数据
基于 Baostock 数据源，纯本地数据库模式
"""

import pandas as pd


class DataFetcher:
    """
    数据获取器

    从本地数据库读取财务数据
    纯本地数据库模式，无需网络连接
    """

    def __init__(self, db_manager=None):
        """
        初始化数据获取器

        Args:
            db_manager: 数据库管理器实例，为None时自动创建
        """
        # 初始化数据库管理器
        if db_manager is None:
            from data_manager import DatabaseManager
            self.db_manager = DatabaseManager()
        else:
            self.db_manager = db_manager

        print("[数据获取器] 使用本地数据库模式")

    def fetch_balance_sheet(self, symbol):
        """
        获取资产负债表

        Args:
            symbol: 股票代码，如 "600519"

        Returns:
            DataFrame: 资产负债表数据
        """
        try:
            data = self.db_manager.get_financial_data(symbol)
            balance = data.get('balance_sheet')
            if balance is not None and not balance.empty:
                return balance
            else:
                print(f"  [警告] {symbol} 无资产负债表数据")
                return None
        except Exception as e:
            print(f"  [错误] 读取资产负债表失败 {symbol}: {e}")
            return None

    def fetch_income_statement(self, symbol):
        """
        获取利润表

        Args:
            symbol: 股票代码

        Returns:
            DataFrame: 利润表数据
        """
        try:
            data = self.db_manager.get_financial_data(symbol)
            income = data.get('income_statement')
            if income is not None and not income.empty:
                return income
            else:
                print(f"  [警告] {symbol} 无利润表数据")
                return None
        except Exception as e:
            print(f"  [错误] 读取利润表失败 {symbol}: {e}")
            return None

    def fetch_cash_flow(self, symbol):
        """
        获取现金流量表

        Args:
            symbol: 股票代码

        Returns:
            DataFrame: 现金流量表数据
        """
        try:
            data = self.db_manager.get_financial_data(symbol)
            cash = data.get('cash_flow')
            if cash is not None and not cash.empty:
                return cash
            else:
                print(f"  [警告] {symbol} 无现金流量表数据")
                return None
        except Exception as e:
            print(f"  [错误] 读取现金流量表失败 {symbol}: {e}")
            return None

    def fetch_financial_abstract(self, symbol):
        """
        获取财务摘要（包含关键指标）

        Args:
            symbol: 股票代码

        Returns:
            DataFrame: 财务摘要数据
        """
        try:
            data = self.db_manager.get_financial_data(symbol)
            abstract = data.get('abstract')
            if abstract is not None and not abstract.empty:
                return abstract
            else:
                print(f"  [警告] {symbol} 无财务摘要数据")
                return None
        except Exception as e:
            print(f"  [错误] 读取财务摘要失败 {symbol}: {e}")
            return None

    def fetch_stock_info(self, symbol):
        """
        获取股票基本信息

        Args:
            symbol: 股票代码

        Returns:
            dict: 股票基本信息
        """
        try:
            info = self.db_manager.get_stock_info(symbol)
            if info:
                return info
            else:
                return {'symbol': symbol, 'name': symbol}
        except Exception as e:
            print(f"  [错误] 读取股票信息失败 {symbol}: {e}")
            return {'symbol': symbol, 'name': symbol}

    def fetch_stock_list(self):
        """
        获取A股所有股票列表

        Returns:
            DataFrame: 股票列表
        """
        try:
            # 从本地数据库获取股票列表
            symbols = self.db_manager.get_all_stocks()
            if symbols:
                df = pd.DataFrame(symbols)
                return df[['symbol', 'name']]
            else:
                print("  [警告] 本地数据库无股票列表")
                return None
        except Exception as e:
            print(f"  [错误] 读取股票列表失败: {e}")
            return None

    def fetch_all_financial_data(self, symbol):
        """
        一次性获取某只股票的所有财务数据

        Args:
            symbol: 股票代码

        Returns:
            dict: 包含所有财务数据的字典
        """
        print(f"\n正在获取 {symbol} 的财务数据...")
        print("  [本地数据库] 读取财务数据...")

        try:
            data = self.db_manager.get_financial_data(symbol)

            # 获取股票名称
            stock_info = self.db_manager.get_stock_info(symbol)
            name = stock_info.get('name', symbol) if stock_info else symbol

            result = {
                'symbol': symbol,
                'name': name,
                'balance_sheet': data.get('balance_sheet'),
                'income_statement': data.get('income_statement'),
                'cash_flow': data.get('cash_flow'),
                'financial_abstract': data.get('abstract'),
                'stock_info': stock_info,
            }

            # 检查是否有数据
            has_data = any([
                result['balance_sheet'] is not None and not result['balance_sheet'].empty,
                result['income_statement'] is not None and not result['income_statement'].empty,
                result['cash_flow'] is not None and not result['cash_flow'].empty,
                result['financial_abstract'] is not None and not result['financial_abstract'].empty,
            ])

            if has_data:
                print(f"  [本地数据库] 读取成功")
            else:
                print(f"  [本地数据库] 无数据，请先运行 download_data.py 下载")

            return result

        except Exception as e:
            print(f"  [本地数据库] 读取失败: {e}")
            return {
                'symbol': symbol,
                'name': symbol,
                'balance_sheet': None,
                'income_statement': None,
                'cash_flow': None,
                'financial_abstract': None,
                'stock_info': None,
            }
