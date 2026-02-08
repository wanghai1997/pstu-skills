# -*- coding: utf-8 -*-
"""
财务指标计算模块
基于《手把手教你读财报》的核心指标计算
"""

import pandas as pd


class FinancialIndicators:
    """
    财务指标计算器

    基于三张财务报表数据计算各项分析指标
    所有方法都处理可能的异常情况，返回None表示无法计算
    """

    @staticmethod
    def safe_float(value, default=0.0):
        """
        安全地将值转换为float

        Args:
            value: 待转换的值
            default: 默认值

        Returns:
            float: 转换后的值
        """
        if value is None or pd.isna(value):
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @classmethod
    def calculate_roe(cls, balance_sheet, income_statement):
        """
        计算ROE（净资产收益率）
        公式：净利润 / 平均净资产

        ROE是唐朝最看重的指标，持续≥15%是优秀企业的标志

        Args:
            balance_sheet: 资产负债表DataFrame
            income_statement: 利润表DataFrame

        Returns:
            float: ROE值，如0.25表示25%
        """
        try:
            if income_statement is None or income_statement.empty:
                return None

            # 获取最近一期净利润
            net_profit = cls.safe_float(income_statement.iloc[0].get('净利润'))

            if balance_sheet is None or balance_sheet.empty:
                return None

            # 获取最近一期所有者权益（净资产）
            latest = balance_sheet.iloc[0]
            equity = cls.safe_float(latest.get('所有者权益(或股东权益)合计'))

            if equity == 0:
                return None

            roe = net_profit / equity
            return round(roe, 4)

        except Exception as e:
            print(f"计算ROE时出错: {e}")
            return None

    @classmethod
    def calculate_gross_margin(cls, income_statement):
        """
        计算毛利率
        公式：(营业收入 - 营业成本) / 营业收入

        毛利率>40%优秀，<20%不投资

        Args:
            income_statement: 利润表DataFrame

        Returns:
            float: 毛利率值
        """
        try:
            if income_statement is None or income_statement.empty:
                return None

            latest = income_statement.iloc[0]
            revenue = cls.safe_float(latest.get('营业收入'))
            cost = cls.safe_float(latest.get('营业成本'))

            if revenue == 0:
                return None

            gross_margin = (revenue - cost) / revenue
            return round(gross_margin, 4)

        except Exception as e:
            print(f"计算毛利率时出错: {e}")
            return None

    @classmethod
    def calculate_net_margin(cls, income_statement):
        """
        计算净利率
        公式：净利润 / 营业收入

        Args:
            income_statement: 利润表DataFrame

        Returns:
            float: 净利率值
        """
        try:
            if income_statement is None or income_statement.empty:
                return None

            latest = income_statement.iloc[0]
            revenue = cls.safe_float(latest.get('营业收入'))
            net_profit = cls.safe_float(latest.get('净利润'))

            if revenue == 0:
                return None

            net_margin = net_profit / revenue
            return round(net_margin, 4)

        except Exception as e:
            print(f"计算净利率时出错: {e}")
            return None

    @classmethod
    def calculate_receivables_ratio(cls, balance_sheet):
        """
        计算应收账款占总资产比例
        公式：(应收账款 + 应收票据) / 总资产

        >30%高度警惕，说明销售回款能力可能有问题

        Args:
            balance_sheet: 资产负债表DataFrame

        Returns:
            float: 应收账款占比
        """
        try:
            if balance_sheet is None or balance_sheet.empty:
                return None

            latest = balance_sheet.iloc[0]

            # 应收账款和应收票据
            receivables = cls.safe_float(latest.get('应收账款'))
            notes_receivable = cls.safe_float(latest.get('应收票据'))
            total_receivables = receivables + notes_receivable

            # 总资产
            total_assets = cls.safe_float(latest.get('资产总计'))

            if total_assets == 0:
                return None

            ratio = total_receivables / total_assets
            return round(ratio, 4)

        except Exception as e:
            print(f"计算应收账款占比时出错: {e}")
            return None

    @classmethod
    def calculate_debt_ratio(cls, balance_sheet):
        """
        计算资产负债率
        公式：总负债 / 总资产

        Args:
            balance_sheet: 资产负债表DataFrame

        Returns:
            float: 资产负债率
        """
        try:
            if balance_sheet is None or balance_sheet.empty:
                return None

            latest = balance_sheet.iloc[0]

            total_liabilities = cls.safe_float(latest.get('负债合计'))
            total_assets = cls.safe_float(latest.get('资产总计'))

            if total_assets == 0:
                return None

            debt_ratio = total_liabilities / total_assets
            return round(debt_ratio, 4)

        except Exception as e:
            print(f"计算资产负债率时出错: {e}")
            return None

    @classmethod
    def calculate_cash_to_debt_ratio(cls, balance_sheet):
        """
        计算货币资金与有息负债比率
        公式：货币资金 / 有息负债

        理想状态≥1，说明现金能覆盖有息负债

        Args:
            balance_sheet: 资产负债表DataFrame

        Returns:
            float: 现金债务比
        """
        try:
            if balance_sheet is None or balance_sheet.empty:
                return None

            latest = balance_sheet.iloc[0]

            # 货币资金
            cash = cls.safe_float(latest.get('货币资金'))

            # 有息负债（短期借款 + 长期借款 + 应付债券）
            short_term_loans = cls.safe_float(latest.get('短期借款'))
            long_term_loans = cls.safe_float(latest.get('长期借款'))
            bonds = cls.safe_float(latest.get('应付债券'))

            interest_bearing_debt = short_term_loans + long_term_loans + bonds

            if interest_bearing_debt == 0:
                # 没有有息负债是好的
                return float('inf')

            ratio = cash / interest_bearing_debt
            return round(ratio, 4)

        except Exception as e:
            print(f"计算现金债务比时出错: {e}")
            return None

    @classmethod
    def calculate_cash_flow_quality(cls, cash_flow, income_statement):
        """
        计算净利润含金量
        公式：经营活动现金流净额 / 净利润

        持续>1是优秀企业特征，<0.5预警

        Args:
            cash_flow: 现金流量表DataFrame
            income_statement: 利润表DataFrame

        Returns:
            float: 净利润含金量
        """
        try:
            if cash_flow is None or cash_flow.empty:
                return None

            if income_statement is None or income_statement.empty:
                return None

            # 经营活动现金流净额
            operating_cf = cls.safe_float(
                cash_flow.iloc[0].get('经营活动产生的现金流量净额')
            )

            # 净利润
            net_profit = cls.safe_float(income_statement.iloc[0].get('净利润'))

            if net_profit == 0:
                return None

            ratio = operating_cf / net_profit
            return round(ratio, 4)

        except Exception as e:
            print(f"计算现金流质量时出错: {e}")
            return None

    @classmethod
    def calculate_expense_ratio(cls, income_statement):
        """
        计算费用率
        公式：(销售费用 + 管理费用 + 财务费用) / 营业收入

        费用率/毛利润>70%危险

        Args:
            income_statement: 利润表DataFrame

        Returns:
            float: 费用率
        """
        try:
            if income_statement is None or income_statement.empty:
                return None

            latest = income_statement.iloc[0]

            revenue = cls.safe_float(latest.get('营业收入'))
            sales_expense = cls.safe_float(latest.get('销售费用'))
            admin_expense = cls.safe_float(latest.get('管理费用'))
            finance_expense = cls.safe_float(latest.get('财务费用'))

            total_expenses = sales_expense + admin_expense + finance_expense

            if revenue == 0:
                return None

            expense_ratio = total_expenses / revenue
            return round(expense_ratio, 4)

        except Exception as e:
            print(f"计算费用率时出错: {e}")
            return None

    @classmethod
    def classify_cash_flow_portrait(cls, cash_flow):
        """
        判断现金流肖像

        根据经营、投资、筹资三类现金流的正负组合
        判断企业类型，"奶牛型"(+--)最理想

        Args:
            cash_flow: 现金流量表DataFrame

        Returns:
            str: 现金流肖像代码，如 "+--"
        """
        try:
            if cash_flow is None or cash_flow.empty:
                return None

            latest = cash_flow.iloc[0]

            # 三类现金流净额
            operating = cls.safe_float(
                latest.get('经营活动产生的现金流量净额')
            )
            investing = cls.safe_float(
                latest.get('投资活动产生的现金流量净额')
            )
            financing = cls.safe_float(
                latest.get('筹资活动产生的现金流量净额')
            )

            # 转换为正负符号
            op_sign = '+' if operating > 0 else '-'
            inv_sign = '+' if investing > 0 else '-'
            fin_sign = '+' if financing > 0 else '-'

            return f"{op_sign}{inv_sign}{fin_sign}"

        except Exception as e:
            print(f"判断现金流肖像时出错: {e}")
            return None

    @classmethod
    def calculate_all_indicators(cls, financial_data):
        """
        一次性计算所有指标

        使用 Baostock 季频数据已计算的指标：
        - roeAvg: ROE净资产收益率
        - gpMargin: 毛利率
        - npMargin: 净利率
        - liabilityToAsset: 资产负债率
        - cfoToNp: 经营现金流与净利润比

        Args:
            financial_data: 包含财务数据的字典
                {
                    'balance_sheet': DataFrame,  # Baostock季频偿债能力数据
                    'income_statement': DataFrame,  # Baostock季频盈利能力数据
                    'cash_flow': DataFrame,  # Baostock季频现金流量数据
                    'financial_abstract': DataFrame  # 财务摘要
                }

        Returns:
            dict: 所有计算出的指标
        """
        balance_sheet = financial_data.get('balance_sheet')  # 季频偿债能力
        income_statement = financial_data.get('income_statement')  # 季频盈利能力
        cash_flow = financial_data.get('cash_flow')  # 季频现金流量
        abstract = financial_data.get('financial_abstract')

        indicators = {}

        # 从 financial_abstract 读取基础指标（如果存在且有效）
        if abstract is not None and not abstract.empty:
            latest = abstract.iloc[0]
            indicators['roe'] = cls.safe_float(latest.get('roe'))
            indicators['gross_margin'] = cls.safe_float(latest.get('gross_margin'))
            indicators['net_margin'] = cls.safe_float(latest.get('net_margin'))
            indicators['debt_ratio'] = cls.safe_float(latest.get('debt_ratio'))
        else:
            indicators['roe'] = None
            indicators['gross_margin'] = None
            indicators['net_margin'] = None
            indicators['debt_ratio'] = None

        # 从季频盈利能力数据读取指标（优先使用，更准确）
        if income_statement is not None and not income_statement.empty:
            latest = income_statement.iloc[0]
            # roeAvg: 净资产收益率平均
            if indicators['roe'] == 0 or indicators['roe'] is None:
                indicators['roe'] = cls.safe_float(latest.get('roeAvg'))
            # gpMargin: 毛利率
            if indicators['gross_margin'] == 0 or indicators['gross_margin'] is None:
                indicators['gross_margin'] = cls.safe_float(latest.get('gpMargin'))
            # npMargin: 净利率
            if indicators['net_margin'] == 0 or indicators['net_margin'] is None:
                indicators['net_margin'] = cls.safe_float(latest.get('npMargin'))

        # 从季频偿债能力数据读取指标
        if balance_sheet is not None and not balance_sheet.empty:
            latest = balance_sheet.iloc[0]
            # liabilityToAsset: 资产负债率
            if indicators['debt_ratio'] == 0 or indicators['debt_ratio'] is None:
                indicators['debt_ratio'] = cls.safe_float(latest.get('liabilityToAsset'))

        # 从季频现金流量数据读取指标
        if cash_flow is not None and not cash_flow.empty:
            latest = cash_flow.iloc[0]
            # cfoToNp: 经营现金流与净利润比（重要指标！）
            indicators['cash_flow_quality'] = cls.safe_float(latest.get('cfoToNp'))
            # 注意：Baostock返回的是现金流量分析指标，不是原始现金流数据
            # 所以无法计算现金流肖像（+--），标记为不可用
            indicators['cash_flow_portrait'] = None
        else:
            indicators['cash_flow_quality'] = None
            indicators['cash_flow_portrait'] = None

        # 以下指标季频数据中没有，需要额外计算或标记为不可用
        indicators['receivables_ratio'] = None  # 季频数据中没有应收账款明细
        indicators['cash_to_debt_ratio'] = None  # 季频数据中没有货币资金和有息负债明细
        indicators['expense_ratio'] = None  # 季频数据中没有三费明细

        return indicators
