# -*- coding: utf-8 -*-
"""
财报筛选器

基于《手把手教你读财报》核心规则的自动化财报分析系统

使用示例:
    from financial_screener import FinancialScreener

    screener = FinancialScreener()
    result = screener.screen_single("600519")

    print(f"股票: {result['name']}")
    print(f"状态: {result['status']}")
    print(f"得分: {result['score']}")
"""

from .screener import FinancialScreener
from .config import SCREENING_CONFIG, CASH_FLOW_PORTRAITS

__version__ = "1.0.0"
__author__ = "wanghai1997"

__all__ = [
    'FinancialScreener',
    'SCREENING_CONFIG',
    'CASH_FLOW_PORTRAITS',
]