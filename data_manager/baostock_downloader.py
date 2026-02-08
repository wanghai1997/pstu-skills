# -*- coding: utf-8 -*-
"""
Baostock 数据下载模块

主数据源：支持日线、周线、分钟线(15/60分钟)及财务数据
优点：免费、稳定、不需要登录、支持分钟级数据
注意：数据T+1更新，分钟线数据有限制
"""

import time
from datetime import datetime, timedelta

import baostock as bs
import pandas as pd

from .database_manager import DatabaseManager


class BaostockDownloader:
    """
    Baostock 数据下载器

    与 AKShare 下载器接口保持一致，方便替换使用
    """

    def __init__(self, db_manager=None):
        self.db = db_manager or DatabaseManager()
        self.lg = None  # Baostock 登录对象

    def _login(self):
        """登录 Baostock"""
        if self.lg is None:
            print("[Baostock] 登录中...")
            self.lg = bs.login()
            if self.lg.error_code != '0':
                print(f"[Baostock] 登录失败: {self.lg.error_msg}")
                return False
            print("[Baostock] 登录成功")
        return True

    def _logout(self):
        """退出 Baostock"""
        if self.lg:
            bs.logout()
            print("[Baostock] 已退出")
            self.lg = None

    def download_hs300_list(self):
        """
        获取沪深300成分股列表

        沪深300指数由上海和深圳证券市场中市值大、流动性好的300只股票组成
        """
        print("\n[Baostock] 获取沪深300成分股列表...")

        if not self._login():
            return []

        try:
            # 查询沪深300成分股
            rs = bs.query_hs300_stocks()

            stocks = []
            while (rs.error_code == '0') & rs.next():
                stocks.append(rs.get_row_data())

            if not stocks:
                print("[Baostock] 未获取到沪深300成分股，回退到全市场列表")
                return self.download_stock_list()

            df = pd.DataFrame(stocks, columns=rs.fields)

            # 简化列名
            df = df[['code', 'code_name']].copy()
            df.columns = ['symbol', 'name']

            # 提取纯数字代码 - 处理多种格式：sh.600000 / sz.000001 / .600000
            # 先去掉 sh. / sz. / bj. 前缀，再去掉可能残留的.
            df['symbol'] = df['symbol'].str.replace(r'^(sh|sz|bj)\.?', '', regex=True)
            # 如果还有点开头的情况，再去掉
            df['symbol'] = df['symbol'].str.lstrip('.')

            # 添加市场标识
            df['market'] = df['symbol'].apply(
                lambda x: 'SH' if str(x).startswith('6') else 'SZ'
            )

            self.db.save_stock_list(df)
            print(f"[Baostock] 沪深300共 {len(df)} 只股票")

            return df['symbol'].tolist()

        except Exception as e:
            print(f"[Baostock] 获取沪深300失败: {e}，回退到全市场列表")
            return self.download_stock_list()

    def download_stock_list(self):
        """下载股票列表"""
        print("\n[Baostock] 获取A股股票列表...")

        if not self._login():
            return []

        try:
            # 获取沪深A股
            rs = bs.query_all_stock(day=datetime.now().strftime('%Y-%m-%d'))

            stocks = []
            while (rs.error_code == '0') & rs.next():
                stocks.append(rs.get_row_data())

            df = pd.DataFrame(stocks, columns=rs.fields)

            # 简化列名
            df = df[['code', 'code_name']].copy()
            df.columns = ['symbol', 'name']

            # 提取纯数字代码
            df['symbol'] = df['symbol'].str.replace(r'^(sh|sz|bj)', '', regex=True)

            # 添加市场标识
            df['market'] = df['symbol'].apply(
                lambda x: 'SH' if x.startswith('6') else 'SZ'
            )

            self.db.save_stock_list(df)
            print(f"[Baostock] 共 {len(df)} 只股票")

            return df['symbol'].tolist()

        except Exception as e:
            print(f"[Baostock] 获取股票列表失败: {e}")
            return []

    def download_daily_prices(self, symbol, years=5):
        """
        下载日线数据

        Args:
            symbol: 股票代码
            years: 下载年数（默认5年，覆盖完整牛熊周期）

        Returns:
            bool: 是否成功
        """
        print(f"  [{symbol}] 下载日线数据 ({years}年)...", end=" ")

        if not self._login():
            return False

        try:
            # 计算起始日期
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years*365)

            # Baostock 需要 sh/sz 前缀
            prefix = 'sh' if symbol.startswith('6') else 'sz'
            code = f"{prefix}.{symbol}"

            rs = bs.query_history_k_data_plus(
                code=code,
                fields='date,open,high,low,close,volume',
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                frequency='d',
                adjustflag='3'  # 复权类型：3为前复权
            )

            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                print("无数据")
                return False

            df = pd.DataFrame(data_list, columns=rs.fields)

            # 转换数据类型
            df['open'] = pd.to_numeric(df['open'], errors='coerce')
            df['high'] = pd.to_numeric(df['high'], errors='coerce')
            df['low'] = pd.to_numeric(df['low'], errors='coerce')
            df['close'] = pd.to_numeric(df['close'], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')

            # 删除无效数据
            df = df.dropna()

            if df.empty:
                print("无有效数据")
                return False

            self.db.save_daily_prices(symbol, df)
            print(f"OK {len(df)} 条")
            return True

        except Exception as e:
            print(f"失败: {e}")
            return False

    def download_weekly_prices(self, symbol, years=5):
        """下载周线数据（默认5年）"""
        print(f"  [{symbol}] 下载周线数据...", end=" ")

        if not self._login():
            return False

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years*365)

            prefix = 'sh' if symbol.startswith('6') else 'sz'
            code = f"{prefix}.{symbol}"

            rs = bs.query_history_k_data_plus(
                code=code,
                fields='date,open,high,low,close,volume',
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                frequency='w',
                adjustflag='3'
            )

            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                print("无数据")
                return False

            df = pd.DataFrame(data_list, columns=rs.fields)

            # 转换数据类型
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df = df.dropna()

            if df.empty:
                print("无有效数据")
                return False

            self.db.save_weekly_prices(symbol, df)
            print(f"OK {len(df)} 条")
            return True

        except Exception as e:
            print(f"失败: {e}")
            return False

    def download_min60_prices(self, symbol, days=30):
        """
        下载60分钟K线数据

        Args:
            symbol: 股票代码
            days: 下载天数，默认30天

        Returns:
            bool: 是否成功
        """
        print(f"  [{symbol}] 下载60分钟数据...", end=" ")

        if not self._login():
            return False

        try:
            # 计算起始日期
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            prefix = 'sh' if symbol.startswith('6') else 'sz'
            code = f"{prefix}.{symbol}"

            # 分钟线字段包含 time
            rs = bs.query_history_k_data_plus(
                code=code,
                fields='date,time,open,high,low,close,volume',
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                frequency='60',  # 60分钟
                adjustflag='3'   # 前复权
            )

            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                print("无数据")
                return False

            df = pd.DataFrame(data_list, columns=rs.fields)

            # 转换数据类型
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # 将 time 字段转换为 datetime 格式
            # Baostock 时间格式为 YYYYMMDDHHMMSS000 (带毫秒)，取前14位
            df['datetime'] = pd.to_datetime(df['time'].str[:14], format='%Y%m%d%H%M%S', errors='coerce')
            df = df.dropna(subset=['datetime'])
            df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]

            df = df.dropna()

            if df.empty:
                print("无有效数据")
                return False

            self.db.save_min60_prices(symbol, df)
            print(f"OK {len(df)} 条")
            return True

        except Exception as e:
            print(f"失败: {e}")
            return False

    def download_min15_prices(self, symbol, days=15):
        """
        下载15分钟K线数据

        Args:
            symbol: 股票代码
            days: 下载天数，默认15天

        Returns:
            bool: 是否成功
        """
        print(f"  [{symbol}] 下载15分钟数据...", end=" ")

        if not self._login():
            return False

        try:
            # 计算起始日期
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            prefix = 'sh' if symbol.startswith('6') else 'sz'
            code = f"{prefix}.{symbol}"

            rs = bs.query_history_k_data_plus(
                code=code,
                fields='date,time,open,high,low,close,volume',
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                frequency='15',  # 15分钟
                adjustflag='3'   # 前复权
            )

            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                print("无数据")
                return False

            df = pd.DataFrame(data_list, columns=rs.fields)

            # 转换数据类型
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # 将 time 字段转换为 datetime 格式
            # Baostock 时间格式为 YYYYMMDDHHMMSS000 (带毫秒)，取前14位
            df['datetime'] = pd.to_datetime(df['time'].str[:14], format='%Y%m%d%H%M%S', errors='coerce')
            df = df.dropna(subset=['datetime'])
            df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']]

            if df.empty:
                print("无有效数据")
                return False

            self.db.save_min15_prices(symbol, df)
            print(f"OK {len(df)} 条")
            return True

        except Exception as e:
            print(f"失败: {e}")
            return False

    def download_financial_data(self, symbol):
        """
        下载财务数据

        使用 Baostock 的季频指标接口：盈利能力、偿债能力、现金流量
        注意：Baostock返回的是已计算的指标，不是原始报表数据
        """
        print(f"  [{symbol}] 下载财务数据...", end=" ")

        if not self._login():
            return False

        try:
            prefix = 'sh' if symbol.startswith('6') else 'sz'
            code = f"{prefix}.{symbol}"

            # 获取最近3年的季度数据
            current_year = datetime.now().year
            profit_data = []      # 季频盈利能力
            balance_data = []     # 季频偿债能力
            cashflow_data = []    # 季频现金流量

            for year in range(current_year - 3, current_year + 1):
                for quarter in range(1, 5):
                    # 1. 季频盈利能力
                    rs_profit = bs.query_profit_data(code=code, year=year, quarter=quarter)
                    while (rs_profit.error_code == '0') & rs_profit.next():
                        profit_data.append(rs_profit.get_row_data())

                    # 2. 季频偿债能力
                    rs_balance = bs.query_balance_data(code=code, year=year, quarter=quarter)
                    while (rs_balance.error_code == '0') & rs_balance.next():
                        balance_data.append(rs_balance.get_row_data())

                    # 3. 季频现金流量
                    rs_cash = bs.query_cash_flow_data(code=code, year=year, quarter=quarter)
                    while (rs_cash.error_code == '0') & rs_cash.next():
                        cashflow_data.append(rs_cash.get_row_data())

                    time.sleep(0.15)  # 避免请求过快

            if not profit_data:
                print("无数据")
                return False

            # 构建 DataFrame
            df_profit = pd.DataFrame(profit_data, columns=rs_profit.fields)
            df_balance = pd.DataFrame(balance_data, columns=rs_balance.fields) if balance_data else None
            df_cash = pd.DataFrame(cashflow_data, columns=rs_cash.fields) if cashflow_data else None

            # 转换数值类型 - 盈利能力指标
            df_profit['roeAvg'] = pd.to_numeric(df_profit.get('roeAvg', 0), errors='coerce')
            df_profit['npMargin'] = pd.to_numeric(df_profit.get('npMargin', 0), errors='coerce')
            df_profit['gpMargin'] = pd.to_numeric(df_profit.get('gpMargin', 0), errors='coerce')
            df_profit['netProfit'] = pd.to_numeric(df_profit.get('netProfit', 0), errors='coerce')

            # 转换数值类型 - 偿债能力指标
            if df_balance is not None:
                df_balance['liabilityToAsset'] = pd.to_numeric(df_balance.get('liabilityToAsset', 0), errors='coerce')

            # 转换数值类型 - 现金流量指标
            if df_cash is not None:
                df_cash['cfoToNp'] = pd.to_numeric(df_cash.get('CFOToNP', 0), errors='coerce')  # 经营现金流与净利润比
                df_cash['cfoToOR'] = pd.to_numeric(df_cash.get('CFOToOR', 0), errors='coerce')  # 经营现金流与营收比

            # 构建摘要数据 - 直接使用Baostock已计算的指标
            abstract_df = pd.DataFrame({
                'symbol': symbol,
                'report_date': df_profit['pubDate'],
                'net_profit': df_profit['netProfit'],
                'revenue': 0,  # 季频数据中没有直接的营业收入
                'eps': 0,      # 季频数据中使用epsTTM替代
                'roe': df_profit['roeAvg'],  # 直接使用Baostock的ROE
                'gross_margin': df_profit['gpMargin'],  # 直接使用Baostock的毛利率
                'net_margin': df_profit['npMargin'],    # 直接使用Baostock的净利率
                'debt_ratio': df_balance['liabilityToAsset'] if df_balance is not None else 0,
                'cash_flow_portrait': '需计算'
            })

            # 保存到数据库 - 同时保存原始季频数据供后续使用
            self.db.save_financial_data(symbol, abstract_df, df_balance, df_profit, df_cash)
            print(f"OK {len(abstract_df)} 期")
            return True

        except Exception as e:
            print(f"失败: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def full_download(self, symbols=None, max_stocks=None, use_conservative=False):
        """
        首次全量下载

        Args:
            symbols: 指定股票列表
            max_stocks: 最多下载几只
            use_conservative: 是否使用保守模式（True=更慢的下载速度，避免限流）
        """
        print("="*70)
        print("Baostock 全量数据下载")
        if use_conservative:
            print("[保守模式] 已启用 - 使用更长的请求间隔以避免限流")
        print("="*70)

        # 获取股票列表
        if symbols is None:
            symbols = self.download_stock_list()

        if max_stocks:
            symbols = symbols[:max_stocks]

        print(f"\n准备下载 {len(symbols)} 只股票的数据:")
        print("  - 日线: 3年历史数据")
        print("  - 周线: 3年历史数据")
        print("  - 60分钟: 最近30天")
        print("  - 15分钟: 最近15天")
        print("  - 财务数据: 最近12期")
        print("="*70)

        # 根据模式设置延时参数
        if use_conservative:
            delay_after_download = 1.0  # 每次下载后休息1秒
            delay_after_stock = 3.0     # 每只股票后休息3秒
            delay_after_batch = 5.0     # 每批后休息5秒
            batch_size = 3              # 每3只暂停一次
            financial_delay = 1.5       # 财务数据后休息1.5秒
        else:
            delay_after_download = 0.5  # 每次下载后休息0.5秒
            delay_after_stock = 2.0     # 每只股票后休息2秒
            delay_after_batch = 5.0     # 每批后休息5秒
            batch_size = 3              # 每3只暂停一次
            financial_delay = 1.0       # 财务数据后休息1秒

        success_count = 0

        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] {symbol}")
            print("-" * 40)

            # 下载日线（5年数据，覆盖完整牛熊周期）
            if self.download_daily_prices(symbol, years=5):
                time.sleep(delay_after_download)

            # 下载周线（5年数据）
            if self.download_weekly_prices(symbol, years=5):
                time.sleep(delay_after_download)

            # 下载60分钟数据（120天，约4个月）
            if self.download_min60_prices(symbol, days=120):
                time.sleep(delay_after_download)

            # 下载15分钟数据（60天，约2个月）
            if self.download_min15_prices(symbol, days=60):
                time.sleep(delay_after_download)

            # 财务数据（每3只下载一次，减少请求）
            if i % 3 == 1:
                self.download_financial_data(symbol)
                time.sleep(financial_delay)

            success_count += 1

            # 每N只暂停一下
            if i % batch_size == 0:
                print(f"  [暂停] 休息{delay_after_batch:.0f}秒...")
                time.sleep(delay_after_batch)

            # 每只股票的额外间隔（保守模式）
            if use_conservative:
                time.sleep(delay_after_stock)

        # 退出登录
        self._logout()

        print("\n" + "="*70)
        print(f"全量下载完成: {success_count}/{len(symbols)} 只股票")
        print("="*70)

        # 打印统计
        stats = self.db.get_data_stats()
        print("\n数据统计:")
        for table, count in stats.items():
            print(f"  {table:20s}: {count:8,} 条")

        return success_count

    def incremental_update(self, symbols=None, delay=1.5):
        """
        每日增量更新

        Baostock 数据T+1更新，只下载最新一天的日线数据

        参数:
            symbols: 要更新的股票列表，None表示更新所有有数据的股票
            delay: 请求间隔时间(秒)，默认1.5秒，避免服务器压力过大
        """
        print("="*70)
        print("Baostock 每日增量更新")
        print(f"请求间隔: {delay}秒/只")
        print("="*70)

        if not self._login():
            return 0

        # 获取有数据的股票列表
        if symbols is None:
            symbols = self.db.get_symbols_with_data()

        if not symbols:
            print("\n本地无数据，请先执行全量下载")
            self._logout()
            return 0

        print(f"\n更新 {len(symbols)} 只股票...")

        updated = 0
        for i, symbol in enumerate(symbols, 1):
            print(f"[{i}/{len(symbols)}] {symbol}...", end=" ")

            try:
                # Baostock 下载最近几天数据
                prefix = 'sh' if symbol.startswith('6') else 'sz'
                code = f"{prefix}.{symbol}"

                rs = bs.query_history_k_data_plus(
                    code,
                    "date,open,high,low,close,volume",
                    start_date=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                    end_date=datetime.now().strftime('%Y-%m-%d'),
                    frequency="d",
                    adjustflag="3"
                )

                data_list = []
                while (rs.error_code == '0') & rs.next():
                    data_list.append(rs.get_row_data())

                if data_list:
                    df = pd.DataFrame(data_list, columns=rs.fields)
                    for col in ['open', 'high', 'low', 'close', 'volume']:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    df = df.dropna()

                    if not df.empty:
                        self.db.save_daily_prices(symbol, df)
                        print(f"OK {len(df)} 条")
                        updated += 1
                    else:
                        print("无新数据")
                else:
                    print("无数据")

                time.sleep(0.3)

            except Exception as e:
                print(f"失败: {e}")

            # 请求间隔，避免服务器压力过大
            time.sleep(delay)

        self._logout()

        print(f"\n更新完成: {updated}/{len(symbols)} 只股票")
        return updated
