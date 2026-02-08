# -*- coding: utf-8 -*-
"""
生成模拟数据用于测试

当 AKShare 无法连接时，使用模拟数据验证本地数据库和分析系统
"""

import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from data_manager import DatabaseManager


def generate_price_series(start_price, days, volatility=0.02, trend=0.0001):
    """
    生成模拟价格序列（随机游走）

    Args:
        start_price: 起始价格
        days: 天数
        volatility: 波动率
        trend: 趋势因子（正数上涨，负数下跌）

    Returns:
        DataFrame with OHLCV data
    """
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    dates = [d for d in dates if d.weekday() < 5]  # 只保留工作日

    prices = [start_price]
    for _ in range(1, len(dates)):
        change = np.random.normal(trend, volatility)
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)

    # 生成 OHLCV
    data = []
    for i, date in enumerate(dates):
        close = prices[i]
        high = close * (1 + abs(np.random.normal(0, 0.01)))
        low = close * (1 - abs(np.random.normal(0, 0.01)))
        open_price = close * (1 + np.random.normal(0, 0.005))
        volume = int(np.random.uniform(1000000, 10000000))

        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        })

    return pd.DataFrame(data)


def generate_minute_data(symbol, days=30, period='60min'):
    """生成分钟级数据"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # 生成交易日
    dates = pd.date_range(start=start_date, end=end_date, freq='B')  # 工作日

    data = []
    base_price = random.uniform(20, 200)

    for date in dates:
        # 每天的交易时间 9:30-11:30, 13:00-15:00
        if period == '60min':
            times = ['09:30', '10:30', '13:00', '14:00']
        else:  # 15min
            times = ['09:30', '09:45', '10:00', '10:15', '10:30', '10:45',
                    '11:00', '11:15', '13:00', '13:15', '13:30', '13:45',
                    '14:00', '14:15', '14:30', '14:45']

        for t in times:
            change = np.random.normal(0, 0.005)
            base_price *= (1 + change)

            data.append({
                'datetime': f"{date.strftime('%Y-%m-%d')} {t}",
                'open': round(base_price * (1 + np.random.normal(0, 0.002)), 2),
                'high': round(base_price * (1 + abs(np.random.normal(0, 0.01))), 2),
                'low': round(base_price * (1 - abs(np.random.normal(0, 0.01))), 2),
                'close': round(base_price, 2),
                'volume': int(np.random.uniform(100000, 1000000))
            })

    return pd.DataFrame(data)


def generate_financial_data(symbol):
    """生成模拟财务数据 - 使用与数据库表匹配的列名"""
    # 生成最近10期财报
    periods = []
    current = datetime.now()
    for i in range(10):
        year = current.year - (i // 4)
        quarter = i % 4 + 1
        periods.append(f"{year}Q{quarter}")

    abstract_data = []
    for period in periods:
        roe = random.uniform(0.10, 0.30)  # ROE 10%-30%
        gross_margin = random.uniform(0.20, 0.60)  # 毛利率 20%-60%
        revenue = random.uniform(1e9, 1e11)
        net_profit = revenue * random.uniform(0.05, 0.25)

        abstract_data.append({
            'symbol': symbol,
            'report_date': period,
            'net_profit': net_profit,
            'revenue': revenue,
            'eps': random.uniform(0.5, 15),
            'roe': roe,
            'gross_margin': gross_margin,
            'net_margin': random.uniform(0.05, 0.30),
            'debt_ratio': random.uniform(0.20, 0.70),
            'cash_flow_portrait': random.choice(['奶牛型(+--)', '成长型(++-)', '稳健型(+-+)']),
        })

    return pd.DataFrame(abstract_data)


def generate_mock_data_for_stocks(symbols, db_path="data/stock_data.db"):
    """
    为指定股票生成模拟数据

    Args:
        symbols: 股票代码列表
        db_path: 数据库路径
    """
    db = DatabaseManager(db_path)

    print("=" * 60)
    print("生成模拟数据")
    print("=" * 60)
    print(f"股票数量: {len(symbols)}")
    print("\n注意：这是模拟数据，仅用于测试代码逻辑！")
    print("=" * 60)

    # 保存股票列表
    stock_list = pd.DataFrame([
        {'symbol': s, 'name': f'股票{s}', 'market': 'SH' if s.startswith('6') else 'SZ'}
        for s in symbols
    ])
    db.save_stock_list(stock_list)

    for symbol in symbols:
        print(f"\n[{symbol}] 生成数据...")

        # 生成不同特征的数据（用于测试不同分析结果）
        if symbol in ['600519', '000858']:  # 白酒 - 高价稳健
            start_price = random.uniform(500, 1500)
            trend = 0.0002
        elif symbol in ['300750', '002594']:  # 新能源 - 高波动
            start_price = random.uniform(100, 500)
            trend = 0.0005
        else:  # 其他 - 普通
            start_price = random.uniform(20, 100)
            trend = 0.0001

        # 日线（3年）
        daily = generate_price_series(start_price, 750, trend=trend)
        db.save_daily_prices(symbol, daily)
        print(f"  日线: {len(daily)} 条")

        # 周线（3年）
        weekly = generate_price_series(start_price, 150, trend=trend)
        db.save_weekly_prices(symbol, weekly)
        print(f"  周线: {len(weekly)} 条")

        # 60分钟（30天）
        min60 = generate_minute_data(symbol, days=30, period='60min')
        db.save_min60_prices(symbol, min60)
        print(f"  60分钟: {len(min60)} 条")

        # 15分钟（15天）
        min15 = generate_minute_data(symbol, days=15, period='15min')
        db.save_min15_prices(symbol, min15)
        print(f"  15分钟: {len(min15)} 条")

        # 财务数据
        financial = generate_financial_data(symbol)
        db.save_financial_data(symbol, financial, None, None, None)
        print(f"  财务数据: {len(financial)} 期")

    print("\n" + "=" * 60)
    print("模拟数据生成完成！")
    print("=" * 60)

    # 显示统计
    stats = db.get_data_stats()
    print("\n数据统计:")
    for table, count in stats.items():
        print(f"  {table:20s}: {count:8,} 条")

    return stats


def main():
    """生成20只股票的模拟数据"""
    watchlist = [
        "600519", "000858", "600809",  # 白酒
        "000333", "000651", "600887", "603288",  # 消费
        "600276", "300760", "600436",  # 医药
        "002415", "300124", "603501",  # 科技
        "300750", "601012", "002594",  # 新能源
        "600036", "601318",  # 金融
        "601899", "600900",  # 其他
    ]

    generate_mock_data_for_stocks(watchlist)


if __name__ == "__main__":
    main()
