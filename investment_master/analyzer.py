# -*- coding: utf-8 -*-
"""
投资大师分析器主类

整合多周期数据获取、技术指标计算和置信度计算
提供统一的投资分析接口
"""

import time

from .config import TRADING_STRATEGY, MULTI_TIMEFRAME_CONFIG
from .data_fetcher import MultiTimeframeDataFetcher
from .indicators import TechnicalIndicators, TrendAnalyzer
from .confidence_engine import ConfidenceEngine


class MasterAnalyzer:
    """
    投资大师分析器

    基于多周期分析和置信度计算的投资决策系统

    使用示例:
        analyzer = MasterAnalyzer()
        result = analyzer.analyze("600519")

        print(f"置信度: {result['confidence']}%")
        print(f"操作建议: {result['action']}")
        print(f"仓位建议: {result['position']}")
    """

    def __init__(self):
        self.data_fetcher = MultiTimeframeDataFetcher()
        self.confidence_engine = ConfidenceEngine()

    def analyze(self, symbol):
        """
        对股票进行完整的投资分析

        Args:
            symbol: 股票代码，如 "600519"

        Returns:
            dict: 完整的分析结果
        """
        print(f"\n{'='*60}")
        print(f"投资大师分析系统 - 分析 {symbol}")
        print('='*60)

        start_time = time.time()

        # 1. 获取股票名称
        stock_name = self.data_fetcher.get_stock_name(symbol)
        print(f"\n股票: {stock_name} ({symbol})")

        # 2. 获取多周期数据
        print("\n【步骤1】获取多周期K线数据...")
        timeframe_data = self.data_fetcher.fetch_all_timeframes(symbol)

        # 3. 计算技术指标
        print("\n【步骤2】计算技术指标...")
        indicators = {}
        timeframe_trends = {}

        for tf_name, data in timeframe_data.items():
            if data is None:
                print(f"  [{tf_name}] 无数据")
                continue

            if isinstance(data, str):
                print(f"  [{tf_name}] 数据错误: {data}")
                continue

            if not hasattr(data, 'empty') or data.empty:
                print(f"  [{tf_name}] 数据为空")
                continue

            # 计算所有技术指标
            indicators[tf_name] = TechnicalIndicators.calculate_all_indicators(data)

            # 分析趋势
            if indicators[tf_name] is not None:
                timeframe_trends[tf_name] = TrendAnalyzer.analyze_trend(indicators[tf_name])

                # 打印趋势
                tf_config = MULTI_TIMEFRAME_CONFIG['periods'].get(tf_name, {})
                tf_display = tf_config.get('name', tf_name)
                weight = tf_config.get('weight', 0)

                trend_info = timeframe_trends[tf_name]
                trend = trend_info.get('trend', 'unknown')
                strength = trend_info.get('strength', 0)

                trend_map = {
                    'strong_bullish': '强势上涨',
                    'bullish': '上涨趋势',
                    'slightly_bullish': '轻微上涨',
                    'neutral': '震荡整理',
                    'slightly_bearish': '轻微下跌',
                    'bearish': '下跌趋势',
                    'strong_bearish': '强势下跌',
                    'unknown': '未知',
                }

                print(f"  [{tf_display:6s} {weight*100:4.0f}%] {trend_map.get(trend, trend):8s} (强度: {strength:3.0f})")

        # 4. 计算置信度
        print("\n【步骤3】计算投资置信度...")
        analysis_data = {
            'symbol': symbol,
            'timeframe_trends': timeframe_trends,
            'indicators': indicators,
        }

        confidence_result = self.confidence_engine.calculate_confidence(analysis_data)
        confidence = confidence_result['total_confidence']

        print(f"\n  综合置信度: {confidence:.1f}%")
        print("\n  各维度评分:")
        for factor, data in confidence_result['breakdown'].items():
            weighted = data['score'] * data['weight']
            print(f"    - {factor:15s}: {data['score']:5.1f} × {data['weight']*100:4.0f}% = {weighted:5.1f}")

        # 5. 生成操作策略
        print("\n【步骤4】生成操作策略...")
        strategy = self._generate_strategy(confidence)

        print(f"\n  建议操作: {strategy['action']}")
        print(f"  仓位建议: {strategy['position_suggestion']}")
        print(f"  止损设置: {strategy['stop_loss']}")
        print(f"  止盈目标: {strategy['take_profit']}")

        # 6. 组装最终结果
        elapsed = time.time() - start_time

        result = {
            'symbol': symbol,
            'name': stock_name,
            'confidence': confidence,
            'confidence_breakdown': confidence_result['breakdown'],
            'action': strategy['action'],
            'position': strategy['position_suggestion'],
            'stop_loss': strategy['stop_loss'],
            'take_profit': strategy['take_profit'],
            'timeframe_trends': timeframe_trends,
            'indicators': {
                tf: {
                    'latest': data.iloc[-1].to_dict() if data is not None and not data.empty else {}
                }
                for tf, data in indicators.items()
            },
            'analysis_time': round(elapsed, 2),
        }

        print(f"\n{'='*60}")
        print(f"分析完成 (用时: {elapsed:.1f}秒)")
        print('='*60)

        return result

    def _generate_strategy(self, confidence):
        """
        根据置信度生成操作策略

        Args:
            confidence: 置信度分数 (0-100)

        Returns:
            dict: 操作策略
        """
        levels = TRADING_STRATEGY['confidence_levels']

        if confidence >= levels['strong_buy']['min_confidence']:
            return levels['strong_buy']
        elif confidence >= levels['buy']['min_confidence']:
            return levels['buy']
        elif confidence >= levels['watch']['min_confidence']:
            return levels['watch']
        elif confidence >= levels['hold']['min_confidence']:
            return levels['hold']
        elif confidence >= levels['reduce']['min_confidence']:
            return levels['reduce']
        else:
            return levels['sell']

    def batch_analyze(self, symbols):
        """
        批量分析多只股票

        Args:
            symbols: 股票代码列表

        Returns:
            list: 各股票的分析结果
        """
        print(f"\n开始批量分析 {len(symbols)} 只股票...")

        results = []
        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] 分析 {symbol}...")
            try:
                result = self.analyze(symbol)
                results.append(result)
            except Exception as e:
                print(f"  分析失败: {e}")
                results.append({
                    'symbol': symbol,
                    'name': 'Error',
                    'confidence': 0,
                    'action': '错误',
                    'error': str(e)
                })

        # 按置信度排序
        results.sort(key=lambda x: x.get('confidence', 0), reverse=True)

        # 打印汇总
        print("\n" + "="*60)
        print("批量分析完成 - 置信度排行榜")
        print("="*60)

        for i, r in enumerate(results[:10], 1):
            conf = r.get('confidence', 0)
            action = r.get('action', '未知')
            name = r.get('name', r.get('symbol', 'Unknown'))
            symbol = r.get('symbol', 'N/A')

            print(f"{i:2d}. {name:12s} ({symbol}) - 置信度: {conf:5.1f}% - {action}")

        return results
