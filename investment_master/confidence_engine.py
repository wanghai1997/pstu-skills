# -*- coding: utf-8 -*-
"""
置信度计算引擎

基于多维度因素计算投资置信度分数
"""

import pandas as pd

from .config import CONFIDENCE_MODEL, get_confidence_weights


class ConfidenceEngine:
    """
    置信度计算引擎

    根据多个维度计算综合置信度分数
    """

    def __init__(self):
        self.weights = get_confidence_weights()

    def calculate_resonance_score(self, timeframe_trends):
        """
        计算多周期共振分数 (30%权重)

        各周期趋势一致性越高，分数越高

        Args:
            timeframe_trends: 各周期趋势分析结果字典
                {
                    'weekly': {'trend': 'bullish', 'strength': 80},
                    'daily': {...},
                    ...
                }

        Returns:
            float: 0-100的共振分数
        """
        if not timeframe_trends:
            return 50

        # 趋势方向映射到数值
        trend_scores = {
            'strong_bullish': 100,
            'bullish': 80,
            'slightly_bullish': 65,
            'neutral': 50,
            'slightly_bearish': 35,
            'bearish': 20,
            'strong_bearish': 0,
        }

        # 计算加权趋势分数
        weighted_sum = 0
        total_weight = 0

        timeframe_weights = {
            'weekly': 0.15,
            'daily': 0.35,
            '60min': 0.30,
            '15min': 0.20,
        }

        for tf, analysis in timeframe_trends.items():
            if analysis and 'trend' in analysis:
                trend = analysis['trend']
                score = trend_scores.get(trend, 50)
                weight = timeframe_weights.get(tf, 0.25)

                weighted_sum += score * weight
                total_weight += weight

        if total_weight == 0:
            return 50

        base_score = weighted_sum / total_weight

        # 趋势一致性加分
        trends = [a['trend'] for a in timeframe_trends.values() if a and 'trend' in a]
        if len(trends) >= 2:
            bullish_count = sum(1 for t in trends if 'bullish' in t)
            bearish_count = sum(1 for t in trends if 'bearish' in t)

            # 如果所有周期都看涨，给予额外加分
            if bullish_count == len(trends):
                base_score = min(base_score * 1.1, 100)
            elif bearish_count == len(trends):
                base_score = base_score * 0.8

        return round(base_score, 2)

    def calculate_pattern_score(self, indicators):
        """
        计算技术形态分数 (20%权重)

        识别经典技术形态并评分

        Args:
            indicators: 各周期技术指标数据

        Returns:
            float: 0-100的形态分数
        """
        scores = []

        for tf, data in indicators.items():
            if data is None or len(data) < 20:
                continue

            latest = data.iloc[-1]
            score = 50  # 基础分

            # 1. 均线多头排列加分
            if all(col in latest for col in ['ma_5', 'ma_10', 'ma_20']):
                if latest['ma_5'] > latest['ma_10'] > latest['ma_20']:
                    score += 15
                elif latest['ma_5'] > latest['ma_20']:
                    score += 5
                elif latest['ma_5'] < latest['ma_10'] < latest['ma_20']:
                    score -= 15

            # 2. 价格在布林带中的位置
            if all(col in latest for col in ['close', 'boll_upper', 'boll_lower']):
                close = latest['close']
                upper = latest['boll_upper']
                lower = latest['boll_lower']

                if upper > lower:
                    position = (close - lower) / (upper - lower)
                    if 0.4 < position < 0.6:  # 在中轨附近，正常
                        score += 5
                    elif position > 0.8:  # 接近上轨，可能超买
                        score -= 5
                    elif position < 0.2:  # 接近下轨，可能超卖
                        score += 10

            # 3. MACD金叉加分
            if 'macd_hist' in data.columns and len(data) >= 3:
                if data['macd_hist'].iloc[-1] > 0 and data['macd_hist'].iloc[-2] <= 0:
                    score += 10  # 金叉
                elif data['macd_hist'].iloc[-1] < 0 and data['macd_hist'].iloc[-2] >= 0:
                    score -= 10  # 死叉

            scores.append(score)

        return round(sum(scores) / len(scores), 2) if scores else 50

    def calculate_volume_price_score(self, indicators):
        """
        计算量价配合分数 (20%权重)

        Args:
            indicators: 各周期技术指标数据

        Returns:
            float: 0-100的量价分数
        """
        scores = []

        for tf, data in indicators.items():
            if data is None or len(data) < 20:
                continue

            if 'volume' not in data.columns or 'volume_ma' not in data.columns:
                continue

            latest = data.iloc[-1]
            recent = data.tail(5)

            score = 50

            # 1. 成交量是否放大
            if latest['volume'] > latest['volume_ma'] * 1.2:
                score += 10
            elif latest['volume'] < latest['volume_ma'] * 0.8:
                score -= 5

            # 2. 价涨量增（上涨放量）
            if len(data) >= 2:
                price_up = latest['close'] > data.iloc[-2]['close']
                volume_up = latest['volume'] > data.iloc[-2]['volume']

                if price_up and volume_up:
                    score += 15  # 价涨量增，健康
                elif price_up and not volume_up:
                    score -= 5   # 价涨量缩，可能动力不足
                elif not price_up and volume_up:
                    score -= 10  # 价跌量增，可能下跌加速

            scores.append(score)

        return round(sum(scores) / len(scores), 2) if scores else 50

    def calculate_momentum_score(self, indicators):
        """
        计算动量强度分数 (20%权重)

        基于RSI、KDJ、MACD计算动量

        Args:
            indicators: 各周期技术指标数据

        Returns:
            float: 0-100的动量分数
        """
        scores = []

        for tf, data in indicators.items():
            if data is None or len(data) < 14:
                continue

            latest = data.iloc[-1]
            score = 50

            # 1. RSI评分
            if 'rsi' in latest:
                rsi = latest['rsi']
                if rsi > 70:
                    score += 10  # 强势，但注意超买
                elif rsi > 60:
                    score += 15  # 健康强势
                elif rsi > 50:
                    score += 5
                elif rsi > 40:
                    score -= 5
                else:
                    score -= 15  # 弱势

            # 2. KDJ评分
            if all(col in latest for col in ['kdj_k', 'kdj_d']):
                k = latest['kdj_k']
                d = latest['kdj_d']

                if k > d:  # K在D上方，金叉状态
                    score += 10
                    if k > 50 and d > 50:
                        score += 5
                else:
                    score -= 10

            # 3. MACD动量
            if 'macd' in latest and 'macd_signal' in latest:
                macd = latest['macd']
                signal = latest['macd_signal']

                if macd > signal:
                    score += 10
                    if macd > 0:
                        score += 5
                else:
                    score -= 10

            scores.append(score)

        return round(sum(scores) / len(scores), 2) if scores else 50

    def calculate_market_factor_score(self, symbol):
        """
        计算市场因素分数 (10%权重)

        考虑大盘环境和板块强度

        Args:
            symbol: 股票代码

        Returns:
            float: 0-100的市场因素分数
        """
        # 简化版本：假设市场环境中性
        # 实际可以实现：获取大盘指数趋势、板块排名等
        return 50

    def calculate_confidence(self, analysis_data):
        """
        计算综合置信度

        Args:
            analysis_data: 分析数据字典，包含：
                {
                    'timeframe_trends': {...},
                    'indicators': {...},
                    'symbol': '600519'
                }

        Returns:
            dict: 置信度详细结果
        """
        # 计算各维度分数
        resonance = self.calculate_resonance_score(
            analysis_data.get('timeframe_trends', {})
        )

        pattern = self.calculate_pattern_score(
            analysis_data.get('indicators', {})
        )

        volume_price = self.calculate_volume_price_score(
            analysis_data.get('indicators', {})
        )

        momentum = self.calculate_momentum_score(
            analysis_data.get('indicators', {})
        )

        market = self.calculate_market_factor_score(
            analysis_data.get('symbol', '')
        )

        # 加权计算综合置信度
        weights = self.weights

        total_confidence = (
            resonance * weights['multi_timeframe_resonance'] +
            pattern * weights['technical_pattern'] +
            volume_price * weights['volume_price'] +
            momentum * weights['momentum'] +
            market * weights['market_factor']
        )

        return {
            'total_confidence': round(total_confidence, 2),
            'breakdown': {
                'resonance': {'score': resonance, 'weight': weights['multi_timeframe_resonance']},
                'pattern': {'score': pattern, 'weight': weights['technical_pattern']},
                'volume_price': {'score': volume_price, 'weight': weights['volume_price']},
                'momentum': {'score': momentum, 'weight': weights['momentum']},
                'market': {'score': market, 'weight': weights['market_factor']},
            }
        }
