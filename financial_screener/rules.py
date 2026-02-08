# -*- coding: utf-8 -*-
"""
筛选规则模块
基于《手把手教你读财报》的规则实现筛选逻辑
"""

from .config import SCREENING_CONFIG, CASH_FLOW_PORTRAITS


class CheckResult:
    """
    单项检查结果

    记录每一项检查的结果、实际值、阈值和建议
    """

    def __init__(self, name, passed, value, threshold, description=""):
        self.name = name
        self.passed = passed  # True/False，是否通过
        self.value = value    # 实际值
        self.threshold = threshold  # 阈值
        self.description = description  # 描述

    def to_dict(self):
        """转换为字典格式"""
        return {
            'name': self.name,
            'passed': self.passed,
            'value': self.value,
            'threshold': self.threshold,
            'description': self.description,
        }


class ScreeningRules:
    """
    筛选规则引擎

    基于唐朝的《手把手教你读财报》规则
    实现各项财务指标的检查和评分
    """

    def __init__(self, config=None):
        """
        初始化筛选规则

        Args:
            config: 自定义配置，None则使用默认配置
        """
        self.config = config or SCREENING_CONFIG

    def check_roe(self, roe):
        """
        检查ROE

        ROE >= 15% 通过
        ROE < 15% 排除

        Args:
            roe: ROE值

        Returns:
            CheckResult: 检查结果
        """
        threshold = self.config['min_roe']

        if roe is None:
            return CheckResult(
                name="ROE",
                passed=False,
                value=None,
                threshold=threshold,
                description="无法获取ROE数据"
            )

        passed = roe >= threshold

        return CheckResult(
            name="ROE",
            passed=passed,
            value=roe,
            threshold=threshold,
            description=f"ROE {'≥' if passed else '<'} {threshold*100:.0f}%"
        )

    def check_gross_margin(self, gross_margin):
        """
        检查毛利率

        毛利率 >= 40% 优秀
        毛利率 >= 20% 通过
        毛利率 < 20% 排除

        Args:
            gross_margin: 毛利率值

        Returns:
            CheckResult: 检查结果
        """
        min_threshold = self.config['min_gross_margin']
        excellent_threshold = self.config.get('excellent_gross_margin', 0.40)

        if gross_margin is None:
            return CheckResult(
                name="毛利率",
                passed=False,
                value=None,
                threshold=min_threshold,
                description="无法获取毛利率数据"
            )

        passed = gross_margin >= min_threshold
        excellent = gross_margin >= excellent_threshold

        description = f"毛利率 {gross_margin*100:.1f}%"
        if excellent:
            description += " (优秀)"
        elif passed:
            description += " (合格)"
        else:
            description += " (过低，建议排除)"

        return CheckResult(
            name="毛利率",
            passed=passed,
            value=gross_margin,
            threshold=min_threshold,
            description=description
        )

    def check_receivables_ratio(self, ratio):
        """
        检查应收账款占比

        比例 <= 30% 通过
        比例 > 30% 预警

        Args:
            ratio: 应收账款占总资产比例

        Returns:
            CheckResult: 检查结果
        """
        threshold = self.config['max_receivables_ratio']

        if ratio is None:
            return CheckResult(
                name="应收账款占比",
                passed=True,  # 无法判断时不作为排除依据
                value=None,
                threshold=threshold,
                description="无法获取应收账款数据"
            )

        passed = ratio <= threshold

        return CheckResult(
            name="应收账款占比",
            passed=passed,
            value=ratio,
            threshold=threshold,
            description=f"应收账款占比 {'≤' if passed else '>'} {threshold*100:.0f}%"
        )

    def check_cash_flow_quality(self, ratio):
        """
        检查现金流质量（净利润含金量）

        经营现金流/净利润 >= 1.0 优秀
        经营现金流/净利润 >= 0.5 通过
        经营现金流/净利润 < 0.5 预警

        Args:
            ratio: 经营现金流/净利润

        Returns:
            CheckResult: 检查结果
        """
        min_threshold = self.config['min_cash_flow_ratio']
        excellent_threshold = self.config.get('excellent_cash_flow_ratio', 1.0)

        if ratio is None:
            return CheckResult(
                name="现金流质量",
                passed=True,  # 无法判断时不作为排除依据
                value=None,
                threshold=min_threshold,
                description="无法获取现金流数据"
            )

        passed = ratio >= min_threshold
        excellent = ratio >= excellent_threshold

        description = f"经营现金流/净利润 = {ratio:.2f}"
        if excellent:
            description += " (优秀)"
        elif passed:
            description += " (合格)"
        else:
            description += " (偏低，需关注)"

        return CheckResult(
            name="现金流质量",
            passed=passed,
            value=ratio,
            threshold=min_threshold,
            description=description
        )

    def check_cash_to_debt_ratio(self, ratio):
        """
        检查现金债务比

        货币资金/有息负债 >= 1.0 通过
        货币资金/有息负债 < 1.0 预警

        Args:
            ratio: 货币资金/有息负债

        Returns:
            CheckResult: 检查结果
        """
        threshold = self.config['min_cash_to_debt_ratio']

        if ratio is None:
            return CheckResult(
                name="现金债务比",
                passed=True,
                value=None,
                threshold=threshold,
                description="无法获取数据"
            )

        # 无穷大表示没有有息负债（这是好事）
        if ratio == float('inf'):
            return CheckResult(
                name="现金债务比",
                passed=True,
                value=float('inf'),
                threshold=threshold,
                description="无有息负债（优秀）"
            )

        passed = ratio >= threshold

        return CheckResult(
            name="现金债务比",
            passed=passed,
            value=ratio,
            threshold=threshold,
            description=f"现金/有息负债 {'≥' if passed else '<'} {threshold}"
        )

    def check_debt_ratio(self, ratio):
        """
        检查资产负债率

        资产负债率不是硬性排除指标，但过高需要警惕
        一般>70%需要关注

        Args:
            ratio: 资产负债率

        Returns:
            CheckResult: 检查结果
        """
        warning_threshold = 0.70  # 70%警戒线

        if ratio is None:
            return CheckResult(
                name="资产负债率",
                passed=True,
                value=None,
                threshold=warning_threshold,
                description="无法获取数据"
            )

        # 资产负债率不是硬性排除，只是预警
        warning = ratio > warning_threshold

        description = f"资产负债率 {ratio*100:.1f}%"
        if warning:
            description += " (偏高，需关注)"
        else:
            description += " (正常)"

        return CheckResult(
            name="资产负债率",
            passed=True,  # 不直接排除
            value=ratio,
            threshold=warning_threshold,
            description=description
        )

    def check_expense_ratio(self, expense_ratio, gross_margin):
        """
        检查费用率

        费用率/毛利润 < 30% 优秀
        费用率/毛利润 < 70% 通过
        费用率/毛利润 >= 70% 危险

        Args:
            expense_ratio: 费用率
            gross_margin: 毛利率

        Returns:
            CheckResult: 检查结果
        """
        threshold = self.config['max_expense_ratio']

        if expense_ratio is None or gross_margin is None or gross_margin == 0:
            return CheckResult(
                name="费用率",
                passed=True,
                value=None,
                threshold=threshold,
                description="无法计算"
            )

        # 计算费用率/毛利润
        ratio_to_margin = expense_ratio / gross_margin if gross_margin > 0 else 0

        passed = ratio_to_margin < threshold

        return CheckResult(
            name="费用率",
            passed=passed,
            value=ratio_to_margin,
            threshold=threshold,
            description=f"费用率/毛利润 = {ratio_to_margin*100:.1f}%"
        )

    def check_cash_flow_portrait(self, portrait):
        """
        检查现金流肖像

        奶牛型(+--)最理想
        妖精型(+++)、骗吃骗喝型(-++)、混吃等死型(-+-)、大出血型(---)需排除

        Args:
            portrait: 现金流肖像代码，如 "+--"

        Returns:
            CheckResult: 检查结果
        """
        if portrait is None:
            return CheckResult(
                name="现金流肖像",
                passed=True,
                value=None,
                threshold=None,
                description="无法获取现金流数据"
            )

        # 获取肖像信息
        portrait_info = CASH_FLOW_PORTRAITS.get(portrait, {
            'name': '未知类型',
            'description': '无法判断',
            'suggestion': '需人工分析'
        })

        # 奶牛型是最理想的
        is_ideal = portrait == '+--'

        # 以下类型建议排除
        exclude_types = ['+++', '-++', '-+-', '---']
        should_exclude = portrait in exclude_types

        return CheckResult(
            name="现金流肖像",
            passed=not should_exclude,
            value=portrait,
            threshold='+--',
            description=f"{portrait_info['name']}({portrait}) - {portrait_info['description']}"
        )

    def apply_all_rules(self, indicators):
        """
        应用所有筛选规则

        Args:
            indicators: 指标字典，包含各项财务指标

        Returns:
            dict: 包含所有检查结果的字典
        """
        results = {
            'checks': {},
            'warnings': [],
            'exclusions': [],
            'score': 0,
            'status': '通过',  # 通过/预警/排除
        }

        # 1. ROE检查（硬性排除）
        roe_check = self.check_roe(indicators.get('roe'))
        results['checks']['roe'] = roe_check.to_dict()
        if not roe_check.passed:
            results['exclusions'].append(f"ROE不达标: {roe_check.description}")

        # 2. 毛利率检查（硬性排除）
        gm_check = self.check_gross_margin(indicators.get('gross_margin'))
        results['checks']['gross_margin'] = gm_check.to_dict()
        if not gm_check.passed:
            results['exclusions'].append(f"毛利率过低: {gm_check.description}")

        # 3. 应收账款占比检查（预警）
        rec_check = self.check_receivables_ratio(indicators.get('receivables_ratio'))
        results['checks']['receivables_ratio'] = rec_check.to_dict()
        if not rec_check.passed:
            results['warnings'].append(f"应收账款占比高: {rec_check.description}")

        # 4. 现金流质量检查（预警）
        cf_check = self.check_cash_flow_quality(indicators.get('cash_flow_quality'))
        results['checks']['cash_flow_quality'] = cf_check.to_dict()
        if not cf_check.passed:
            results['warnings'].append(f"现金流质量差: {cf_check.description}")

        # 5. 现金债务比检查（预警）
        ctd_check = self.check_cash_to_debt_ratio(indicators.get('cash_to_debt_ratio'))
        results['checks']['cash_to_debt_ratio'] = ctd_check.to_dict()
        if not ctd_check.passed:
            results['warnings'].append(f"现金覆盖不足: {ctd_check.description}")

        # 6. 资产负债率检查（参考）
        debt_check = self.check_debt_ratio(indicators.get('debt_ratio'))
        results['checks']['debt_ratio'] = debt_check.to_dict()

        # 7. 费用率检查（预警）
        exp_check = self.check_expense_ratio(
            indicators.get('expense_ratio'),
            indicators.get('gross_margin')
        )
        results['checks']['expense_ratio'] = exp_check.to_dict()
        if not exp_check.passed:
            results['warnings'].append(f"费用率过高: {exp_check.description}")

        # 8. 现金流肖像检查
        portrait_check = self.check_cash_flow_portrait(indicators.get('cash_flow_portrait'))
        results['checks']['cash_flow_portrait'] = portrait_check.to_dict()
        if not portrait_check.passed:
            results['exclusions'].append(f"现金流异常: {portrait_check.description}")

        # 计算综合得分
        passed_count = sum(1 for c in results['checks'].values() if c['passed'])
        total_count = len(results['checks'])
        results['score'] = int((passed_count / total_count) * 100) if total_count > 0 else 0

        # 确定最终状态
        if results['exclusions']:
            results['status'] = '排除'
        elif results['warnings']:
            results['status'] = '预警'
        else:
            results['status'] = '通过'

        return results
