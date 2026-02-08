# -*- coding: utf-8 -*-
"""
投资大师分析系统

基于多周期分析和置信度计算的智能投资决策系统

使用示例:
    from investment_master import MasterAnalyzer

    analyzer = MasterAnalyzer()
    result = analyzer.analyze("600519")

    print(f"置信度: {result['confidence']}%")
    print(f"操作建议: {result['action']}")
    print(f"仓位建议: {result['position']}")
"""

from .analyzer import MasterAnalyzer

__version__ = "1.0.0"
__author__ = "wanghai1997"

__all__ = ['MasterAnalyzer']
