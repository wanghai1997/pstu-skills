# -*- coding: utf-8 -*-
"""
主筛选器模块
整合数据获取、指标计算和规则检查，提供统一的筛选接口
"""

from .data_fetcher import DataFetcher
from .indicators import FinancialIndicators
from .rules import ScreeningRules


class FinancialScreener:
    """
    财报筛选器主类

    这是整个系统的入口类，提供简洁的API进行股票筛选
    使用示例：
        screener = FinancialScreener()
        result = screener.screen_single("600519")
    """

    def __init__(self, db_manager=None):
        """
        初始化筛选器

        Args:
            db_manager: 数据库管理器实例，为None时自动创建
        """
        self.data_fetcher = DataFetcher(db_manager=db_manager)
        self.rules = ScreeningRules()

    def screen_single(self, symbol):
        """
        对单只股票进行深度筛选

        Args:
            symbol: 股票代码，如 "600519"

        Returns:
            dict: 筛选结果，包含状态、得分、各项指标等
        """
        print(f"\n{'='*60}")
        print(f"正在分析股票: {symbol}")
        print('='*60)

        # 1. 获取所有财务数据
        financial_data = self.data_fetcher.fetch_all_financial_data(symbol)

        if financial_data is None:
            return {
                'symbol': symbol,
                'name': 'Unknown',
                'status': '错误',
                'error': '无法获取财务数据',
                'score': 0,
            }

        # 2. 计算所有指标
        print("\n正在计算财务指标...")
        indicators = FinancialIndicators.calculate_all_indicators(financial_data)

        # 打印指标（调试用）
        for name, value in indicators.items():
            if value is not None:
                if isinstance(value, float) and value != float('inf'):
                    print(f"  {name}: {value:.4f}")
                else:
                    print(f"  {name}: {value}")

        # 3. 应用筛选规则
        print("\n正在应用筛选规则...")
        rule_results = self.rules.apply_all_rules(indicators)

        # 4. 组装最终结果
        result = {
            'symbol': symbol,
            'name': financial_data.get('name', symbol),
            'status': rule_results['status'],
            'score': rule_results['score'],
            'indicators': indicators,
            'checks': rule_results['checks'],
            'warnings': rule_results['warnings'],
            'exclusions': rule_results['exclusions'],
        }

        # 5. 打印结果摘要
        print(f"\n{'='*60}")
        print(f"筛选结果摘要")
        print('='*60)
        print(f"股票: {result['name']} ({symbol})")
        print(f"状态: {result['status']}")
        print(f"综合得分: {result['score']}/100")

        if result['exclusions']:
            print(f"\n排除原因:")
            for exclusion in result['exclusions']:
                print(f"  - {exclusion}")

        if result['warnings']:
            print(f"\n风险提示:")
            for warning in result['warnings']:
                print(f"  - {warning}")

        if result['status'] == '通过':
            print(f"\n[OK] 该股票通过所有筛选条件")

        return result

    def screen_batch(self, symbols):
        """
        批量筛选多只股票

        Args:
            symbols: 股票代码列表，如 ["600519", "000001", "000858"]

        Returns:
            list: 每只股票的筛选结果列表
        """
        print(f"\n开始批量筛选 {len(symbols)} 只股票...")
        print(f"股票列表: {', '.join(symbols)}")

        results = []
        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] 正在分析 {symbol}...")
            result = self.screen_single(symbol)
            results.append(result)

        # 打印汇总
        print(f"\n{'='*60}")
        print(f"批量筛选完成")
        print('='*60)

        passed = [r for r in results if r['status'] == '通过']
        warning = [r for r in results if r['status'] == '预警']
        excluded = [r for r in results if r['status'] == '排除']

        print(f"总计: {len(results)} 只")
        print(f"  通过: {len(passed)} 只")
        print(f"  预警: {len(warning)} 只")
        print(f"  排除: {len(excluded)} 只")

        if passed:
            print(f"\n通过筛选的股票:")
            for r in passed:
                print(f"  [OK] {r['name']} ({r['symbol']}) - 得分: {r['score']}")

        return results

    def screen_by_industry(self, industry_codes, limit=20):
        """
        按行业筛选股票（预留接口）

        Args:
            industry_codes: 行业代码列表
            limit: 最多筛选数量

        Returns:
            list: 筛选结果
        """
        # TODO: 实现按行业筛选
        # 需要AKShare的行业分类接口
        print("按行业筛选功能待实现")
        return []

    def get_cache_info(self):
        """
        获取缓存信息

        Returns:
            dict: 缓存统计信息
        """
        return self.data_fetcher.get_cache_info()

    def clear_cache(self, symbol=None, data_type=None):
        """
        清除缓存

        Args:
            symbol: 股票代码，None则清除所有
            data_type: 数据类型，None则清除该股票所有类型

        Returns:
            int: 清除的文件数量
        """
        return self.data_fetcher.clear_cache(symbol, data_type)
