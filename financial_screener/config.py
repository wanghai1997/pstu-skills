# -*- coding: utf-8 -*-
"""
财报筛选器配置文件
基于《手把手教你读财报》核心规则定义筛选阈值
"""

# ==================== 筛选阈值配置 ====================
# 这些阈值基于唐朝的《手把手教你读财报》
# 可以根据个人投资策略调整

SCREENING_CONFIG = {
    # ========== 硬性排除标准 ==========
    # ROE（净资产收益率）低于15%直接排除
    # 唐朝认为ROE是衡量企业盈利能力的核心指标
    "min_roe": 0.15,  # 15%

    # 上市时间少于5年排除
    # 原因：上市前数据通常被美化，需要观察上市后真实表现
    "min_listing_years": 5,

    # ========== 预警阈值 ==========
    # 应收账款/总资产超过30%高度警惕
    # 说明：应收账款增幅不应超过营收增幅
    "max_receivables_ratio": 0.30,  # 30%

    # 经营现金流/净利润低于0.5预警
    # 说明：持续低于1说明利润含金量不足
    "min_cash_flow_ratio": 0.5,  # 50%

    # 货币资金/有息负债低于1预警
    # 说明：理想状态是现金能覆盖有息负债
    "min_cash_to_debt_ratio": 1.0,  # 100%

    # 毛利率低于20%不投资
    # 说明：毛利率反映产品竞争力
    "min_gross_margin": 0.20,  # 20%

    # 费用率/毛利润超过70%危险
    # 说明：费用率过高侵蚀利润
    "max_expense_ratio": 0.70,  # 70%

    # ========== 优秀标准（加分项） ==========
    # 毛利率超过40%视为优秀
    "excellent_gross_margin": 0.40,  # 40%

    # 经营现金流/净利润持续大于1是优秀企业特征
    "excellent_cash_flow_ratio": 1.0,  # 100%
}


# ==================== 数据配置 ====================
DATA_CONFIG = {
    # 缓存目录
    "cache_dir": "data/cache",

    # 缓存有效期（天）
    "cache_valid_days": {
        "balance_sheet": 30,      # 资产负债表：月度更新
        "income_statement": 30,   # 利润表：月度更新
        "cash_flow": 30,          # 现金流量表：月度更新
        "spot_quote": 1,          # 实时行情：每日更新
    },

    # AKShare接口重试次数
    "max_retries": 3,

    # 重试间隔（秒）
    "retry_delay": 2,
}


# ==================== 报告配置 ====================
REPORT_CONFIG = {
    # 输出文件名
    "excel_filename": "financial_screening_report.xlsx",

    # 文本报告列宽
    "text_report_width": 80,

    # 显示的检查项
    "display_checks": [
        "roe",
        "gross_margin",
        "receivables_ratio",
        "cash_flow_ratio",
        "debt_ratio",
        "cash_to_debt_ratio",
    ],
}


# ==================== 现金流肖像配置 ====================
# 根据经营/投资/筹资现金流正负组合判断企业类型
CASH_FLOW_PORTRAITS = {
    "+++": {"name": "妖精型", "description": "有钱还筹资，需警惕", "suggestion": "调查筹资用途"},
    "++-": {"name": "老母鸡型", "description": "成熟期，关注股息率", "suggestion": "适合收息投资者"},
    "+-+": {"name": "蛮牛型", "description": "扩张期，看项目前景", "suggestion": "深入研究扩张项目"},
    "+--": {"name": "奶牛型", "description": "最理想类型", "suggestion": "重点关注"},
    "-++": {"name": "骗吃骗喝型", "description": "远离", "suggestion": "直接排除"},
    "-+-": {"name": "混吃等死型", "description": "远离", "suggestion": "直接排除"},
    "--+": {"name": "赌徒型", "description": "高风险", "suggestion": "谨慎对待"},
    "---": {"name": "大出血型", "description": "拒绝参与", "suggestion": "直接排除"},
}


def get_config():
    """
    获取完整配置
    返回包含所有配置项的字典
    """
    return {
        "screening": SCREENING_CONFIG,
        "data": DATA_CONFIG,
        "report": REPORT_CONFIG,
        "cash_flow_portraits": CASH_FLOW_PORTRAITS,
    }


def get_screening_threshold(key):
    """
    获取特定筛选阈值

    Args:
        key: 阈值键名，如 "min_roe", "max_receivables_ratio"

    Returns:
        阈值数值

    Example:
        >>> roe_threshold = get_screening_threshold("min_roe")
        >>> print(roe_threshold)  # 0.15
    """
    return SCREENING_CONFIG.get(key)
