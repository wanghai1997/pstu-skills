# -*- coding: utf-8 -*-
"""
投资大师分析系统配置

多周期分析和置信度计算模型的参数配置
"""

# ==================== 多周期分析配置 ====================
MULTI_TIMEFRAME_CONFIG = {
    "periods": {
        "weekly": {
            "name": "周线",
            "weight": 0.15,  # 15%权重
            "period": "weekly",
            "description": "判断主要趋势",
            "ma_periods": [10, 20, 60],  # 均线周期（周）
        },
        "daily": {
            "name": "日线",
            "weight": 0.35,  # 35%权重
            "period": "daily",
            "description": "判断中期趋势",
            "ma_periods": [5, 10, 20, 60],  # 均线周期（日）
        },
        "60min": {
            "name": "60分钟",
            "weight": 0.30,  # 30%权重
            "period": "60min",
            "description": "精确入场点",
            "ma_periods": [10, 20, 60],  # 均线周期
        },
        "15min": {
            "name": "15分钟",
            "weight": 0.20,  # 20%权重
            "period": "15min",
            "description": "短线确认",
            "ma_periods": [10, 20],  # 均线周期
        },
    },
    "data_days": {
        "weekly": 500,   # 周线需要500天数据（约100周）
        "daily": 250,    # 日线需要250天（1年）
        "60min": 60,     # 60分钟需要60天
        "15min": 30,     # 15分钟需要30天
    }
}

# ==================== 置信度计算模型配置 ====================
CONFIDENCE_MODEL = {
    "factors": {
        "multi_timeframe_resonance": {
            "name": "多周期共振",
            "weight": 0.30,  # 30%权重
            "description": "各周期趋势一致性",
        },
        "technical_pattern": {
            "name": "技术形态",
            "weight": 0.20,  # 20%权重
            "description": "识别经典技术形态",
        },
        "volume_price": {
            "name": "量价配合",
            "weight": 0.20,  # 20%权重
            "description": "成交量与价格配合度",
        },
        "momentum": {
            "name": "动量强度",
            "weight": 0.20,  # 20%权重
            "description": "RSI、MACD、KDJ等指标",
        },
        "market_factor": {
            "name": "市场因素",
            "weight": 0.10,  # 10%权重
            "description": "大盘环境、板块强度",
        },
    }
}

# ==================== 技术指标阈值配置 ====================
TECHNICAL_INDICATORS = {
    "RSI": {
        "period": 14,
        "overbought": 70,   # 超买线
        "oversold": 30,     # 超卖线
        "strong_threshold": 60,  # 强势阈值
        "weak_threshold": 40,    # 弱势阈值
    },
    "MACD": {
        "fast": 12,
        "slow": 26,
        "signal": 9,
    },
    "KDJ": {
        "n": 9,
        "m1": 3,
        "m2": 3,
        "overbought": 80,
        "oversold": 20,
    },
    "BOLLINGER": {
        "period": 20,
        "std_dev": 2,
    },
    "VOLUME": {
        "ma_period": 20,  # 成交量均线周期
        "spike_threshold": 1.5,  # 放量阈值（均量1.5倍以上）
    }
}

# ==================== 趋势判断标准 ====================
TREND_STANDARDS = {
    "strong_bullish": {
        "description": "强势上涨",
        "ma_alignment": "short > medium > long",  # 均线多头排列
        "price_vs_ma": "above_all",  # 价格在所有均线上方
        "rsi_min": 50,
    },
    "bullish": {
        "description": "上涨趋势",
        "ma_alignment": "short > long",  # 短期在长期上方
        "price_vs_ma": "above_major",  # 价格在主要均线上方
        "rsi_min": 45,
    },
    "neutral": {
        "description": "震荡整理",
        "ma_alignment": "mixed",  # 均线缠绕
        "rsi_range": [40, 60],
    },
    "bearish": {
        "description": "下跌趋势",
        "ma_alignment": "short < long",
        "price_vs_ma": "below_major",
        "rsi_max": 55,
    },
    "strong_bearish": {
        "description": "强势下跌",
        "ma_alignment": "short < medium < long",  # 均线空头排列
        "price_vs_ma": "below_all",
        "rsi_max": 40,
    },
}

# ==================== 操作策略配置 ====================
TRADING_STRATEGY = {
    "confidence_levels": {
        "strong_buy": {
            "min_confidence": 80,
            "action": "强烈买入",
            "position_suggestion": "50-70%",
            "stop_loss": "-8%",
            "take_profit": "+20%",
        },
        "buy": {
            "min_confidence": 65,
            "action": "买入",
            "position_suggestion": "30-50%",
            "stop_loss": "-6%",
            "take_profit": "+15%",
        },
        "watch": {
            "min_confidence": 50,
            "action": "观望",
            "position_suggestion": "10-20%",
            "stop_loss": "-5%",
            "take_profit": "+10%",
        },
        "hold": {
            "min_confidence": 40,
            "action": "持有",
            "position_suggestion": "维持现状",
            "stop_loss": "-10%",
            "take_profit": "灵活",
        },
        "reduce": {
            "min_confidence": 25,
            "action": "减仓",
            "position_suggestion": "减仓至30%",
            "stop_loss": "立即执行",
            "take_profit": "不适用",
        },
        "sell": {
            "min_confidence": 0,
            "action": "卖出",
            "position_suggestion": "清仓",
            "stop_loss": "已触发",
            "take_profit": "不适用",
        },
    }
}


def get_confidence_weights():
    """
    获取置信度计算权重
    用于计算综合置信度分数
    """
    factors = CONFIDENCE_MODEL["factors"]
    return {
        name: config["weight"]
        for name, config in factors.items()
    }


def get_timeframe_weights():
    """
    获取多周期权重
    用于计算加权趋势分数
    """
    periods = MULTI_TIMEFRAME_CONFIG["periods"]
    return {
        name: config["weight"]
        for name, config in periods.items()
    }
