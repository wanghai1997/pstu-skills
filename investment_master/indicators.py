# -*- coding: utf-8 -*-
"""
技术指标计算模块

计算各种技术分析指标：MA、MACD、RSI、KDJ、布林带等
"""

import numpy as np
import pandas as pd


class TechnicalIndicators:
    """
    技术指标计算器
    """

    @staticmethod
    def calculate_ma(data, periods):
        """
        计算简单移动平均线 (SMA)

        Args:
            data: DataFrame或价格序列
            periods: 周期列表，如 [5, 10, 20]

        Returns:
            DataFrame: 包含各周期MA的数据
        """
        if isinstance(data, pd.DataFrame):
            close = data['close']
            result = data.copy()
        else:
            close = data
            result = pd.DataFrame({'close': close})

        for period in periods:
            result[f'ma_{period}'] = close.rolling(window=period).mean()

        return result

    @staticmethod
    def calculate_ema(data, period):
        """
        计算指数移动平均线 (EMA)

        Args:
            data: 价格序列
            period: 周期

        Returns:
            Series: EMA值
        """
        return data.ewm(span=period, adjust=False).mean()

    @classmethod
    def calculate_macd(cls, data, fast=12, slow=26, signal=9):
        """
        计算MACD指标

        Args:
            data: DataFrame或价格序列
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            DataFrame: 包含macd, signal, histogram
        """
        if isinstance(data, pd.DataFrame):
            close = data['close']
        else:
            close = data

        # 计算EMA
        ema_fast = cls.calculate_ema(close, fast)
        ema_slow = cls.calculate_ema(close, slow)

        # MACD线
        macd_line = ema_fast - ema_slow

        # 信号线
        signal_line = cls.calculate_ema(macd_line, signal)

        # 柱状图
        histogram = macd_line - signal_line

        return pd.DataFrame({
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        })

    @staticmethod
    def calculate_rsi(data, period=14):
        """
        计算RSI相对强弱指标

        Args:
            data: DataFrame或价格序列
            period: 周期，默认14

        Returns:
            Series: RSI值
        """
        if isinstance(data, pd.DataFrame):
            close = data['close']
        else:
            close = data

        # 计算价格变化
        delta = close.diff()

        # 分离上涨和下跌
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # 计算RS和RSI
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @classmethod
    def calculate_kdj(cls, data, n=9, m1=3, m2=3):
        """
        计算KDJ指标

        Args:
            data: DataFrame，需要包含high, low, close
            n: RSV周期
            m1: K值平滑周期
            m2: D值平滑周期

        Returns:
            DataFrame: 包含K, D, J值
        """
        low_list = data['low'].rolling(window=n, min_periods=n).min()
        high_list = data['high'].rolling(window=n, min_periods=n).max()

        rsv = (data['close'] - low_list) / (high_list - low_list) * 100

        k = rsv.ewm(com=m1-1, adjust=False).mean()
        d = k.ewm(com=m2-1, adjust=False).mean()
        j = 3 * k - 2 * d

        return pd.DataFrame({
            'k': k,
            'd': d,
            'j': j
        })

    @staticmethod
    def calculate_bollinger(data, period=20, std_dev=2):
        """
        计算布林带 (Bollinger Bands)

        Args:
            data: DataFrame或价格序列
            period: 周期
            std_dev: 标准差倍数

        Returns:
            DataFrame: 包含upper, middle, lower
        """
        if isinstance(data, pd.DataFrame):
            close = data['close']
        else:
            close = data

        middle = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return pd.DataFrame({
            'upper': upper,
            'middle': middle,
            'lower': lower
        })

    @classmethod
    def calculate_all_indicators(cls, df):
        """
        一次性计算所有技术指标

        Args:
            df: DataFrame，包含open, high, low, close, volume

        Returns:
            DataFrame: 原始数据加上所有技术指标
        """
        if df is None or df.empty:
            return None

        result = df.copy()

        # 1. 计算MA（多种周期）
        result = cls.calculate_ma(result, [5, 10, 20, 60])

        # 2. 计算MACD
        macd_df = cls.calculate_macd(result)
        result['macd'] = macd_df['macd']
        result['macd_signal'] = macd_df['signal']
        result['macd_hist'] = macd_df['histogram']

        # 3. 计算RSI
        result['rsi'] = cls.calculate_rsi(result)

        # 4. 计算KDJ
        kdj_df = cls.calculate_kdj(result)
        result['kdj_k'] = kdj_df['k']
        result['kdj_d'] = kdj_df['d']
        result['kdj_j'] = kdj_df['j']

        # 5. 计算布林带
        boll_df = cls.calculate_bollinger(result)
        result['boll_upper'] = boll_df['upper']
        result['boll_middle'] = boll_df['middle']
        result['boll_lower'] = boll_df['lower']

        # 6. 计算成交量MA
        if 'volume' in result.columns:
            result['volume_ma'] = result['volume'].rolling(window=20).mean()

        return result


class TrendAnalyzer:
    """
    趋势分析器

    基于技术指标判断趋势方向和强度
    """

    @staticmethod
    def analyze_trend(df):
        """
        分析趋势

        Args:
            df: DataFrame，包含技术指标

        Returns:
            dict: 趋势分析结果
        """
        if df is None or len(df) < 20:
            return {'trend': 'unknown', 'strength': 0}

        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest

        # 1. 均线多头排列判断
        ma_bullish = False
        if all(col in latest for col in ['ma_5', 'ma_10', 'ma_20']):
            ma_bullish = latest['ma_5'] > latest['ma_10'] > latest['ma_20']

        # 2. 价格在均线上方
        price_above_ma = False
        if 'ma_20' in latest:
            price_above_ma = latest['close'] > latest['ma_20']

        # 3. MACD判断
        macd_bullish = False
        if 'macd' in latest and 'macd_signal' in latest:
            macd_bullish = latest['macd'] > latest['macd_signal']

        # 4. RSI判断
        rsi_strong = False
        if 'rsi' in latest:
            rsi_strong = latest['rsi'] > 50

        # 综合判断趋势
        bullish_signals = sum([ma_bullish, price_above_ma, macd_bullish, rsi_strong])

        if bullish_signals >= 3:
            trend = 'bullish'
            strength = 80 + (bullish_signals - 3) * 10
        elif bullish_signals >= 2:
            trend = 'slightly_bullish'
            strength = 60
        elif bullish_signals == 1:
            trend = 'neutral'
            strength = 50
        else:
            trend = 'bearish'
            strength = 30

        return {
            'trend': trend,
            'strength': min(strength, 100),
            'signals': {
                'ma_bullish': ma_bullish,
                'price_above_ma': price_above_ma,
                'macd_bullish': macd_bullish,
                'rsi_strong': rsi_strong,
            }
        }

    @staticmethod
    def detect_support_resistance(df, window=20):
        """
        简单支撑阻力位检测

        Args:
            df: DataFrame
            window: 观察窗口

        Returns:
            dict: 支撑和阻力位
        """
        if df is None or len(df) < window:
            return {'support': None, 'resistance': None}

        recent = df.tail(window)

        # 简单方法：取近期高低点
        resistance = recent['high'].max()
        support = recent['low'].min()

        return {
            'support': support,
            'resistance': resistance,
            'current': df.iloc[-1]['close']
        }
