# -*- coding: utf-8 -*-
"""
测试 Baostock 分钟数据下载功能
验证新的纯 Baostock 架构是否工作
"""

import baostock as bs
import pandas as pd
from datetime import datetime, timedelta

def test_baostock_login():
    """测试登录"""
    print("="*60)
    print("测试 Baostock 登录")
    print("="*60)

    lg = bs.login()
    if lg.error_code == '0':
        print("[OK] 登录成功")
        return True
    else:
        print(f"[ERR] 登录失败: {lg.error_msg}")
        return False

def test_daily_data(symbol="600519"):
    """测试日线数据"""
    print("\n" + "="*60)
    print(f"测试日线数据 - {symbol}")
    print("="*60)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    prefix = 'sh' if symbol.startswith('6') else 'sz'
    code = f"{prefix}.{symbol}"

    rs = bs.query_history_k_data_plus(
        code=code,
        fields='date,open,high,low,close,volume',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        frequency='d',
        adjustflag='3'
    )

    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())

    if data_list:
        df = pd.DataFrame(data_list, columns=rs.fields)
        print(f"[OK] 获取 {len(df)} 条日线数据")
        print("\n前3条数据:")
        print(df.head(3).to_string())
        return True
    else:
        print("[ERR] 无数据")
        return False

def test_minute_data(symbol="600519", period="60"):
    """测试分钟数据"""
    print(f"\n" + "="*60)
    print(f"测试 {period}分钟数据 - {symbol}")
    print("="*60)

    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)  # 只取最近5天

    prefix = 'sh' if symbol.startswith('6') else 'sz'
    code = f"{prefix}.{symbol}"

    rs = bs.query_history_k_data_plus(
        code=code,
        fields='date,time,open,high,low,close,volume',
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d'),
        frequency=period,
        adjustflag='3'
    )

    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())

    if data_list:
        df = pd.DataFrame(data_list, columns=rs.fields)
        print(f"[OK] 获取 {len(df)} 条{period}分钟数据")

        # 转换时间格式 - Baostock 时间格式为 YYYYMMDDHHMMSS000 (带毫秒)
        df['datetime'] = pd.to_datetime(df['time'].str[:14], format='%Y%m%d%H%M%S', errors='coerce')
        df = df.dropna(subset=['datetime'])
        print("\n前3条数据:")
        print(df[['datetime', 'open', 'close', 'volume']].head(3).to_string())
        return True
    else:
        print("[ERR] 无数据")
        return False

def test_financial_data(symbol="600519"):
    """测试财务数据"""
    print(f"\n" + "="*60)
    print(f"测试财务数据 - {symbol}")
    print("="*60)

    prefix = 'sh' if symbol.startswith('6') else 'sz'
    code = f"{prefix}.{symbol}"

    # 获取最近一季度数据
    current_year = datetime.now().year

    # 利润表
    rs_profit = bs.query_profit_data(code=code, year=current_year, quarter=3)
    profit_data = []
    while (rs_profit.error_code == '0') & rs_profit.next():
        profit_data.append(rs_profit.get_row_data())

    # 资产负债表
    rs_balance = bs.query_balance_data(code=code, year=current_year, quarter=3)
    balance_data = []
    while (rs_balance.error_code == '0') & rs_balance.next():
        balance_data.append(rs_balance.get_row_data())

    # 现金流量表
    rs_cash = bs.query_cash_flow_data(code=code, year=current_year, quarter=3)
    cash_data = []
    while (rs_cash.error_code == '0') & rs_cash.next():
        cash_data.append(rs_cash.get_row_data())

    print(f"[OK] 利润表: {len(profit_data)} 条")
    print(f"[OK] 资产负债表: {len(balance_data)} 条")
    print(f"[OK] 现金流量表: {len(cash_data)} 条")

    if profit_data:
        df_profit = pd.DataFrame(profit_data, columns=rs_profit.fields)
        print("\n利润表字段:", list(df_profit.columns))

    return True

def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("Baostock 数据源测试")
    print("验证纯 Baostock 架构是否支持所有需求")
    print("="*60)

    results = []

    # 1. 登录测试
    if test_baostock_login():
        results.append(("登录", True))

        # 2. 日线数据
        results.append(("日线数据", test_daily_data("600519")))

        # 3. 60分钟数据
        results.append(("60分钟数据", test_minute_data("600519", "60")))

        # 4. 15分钟数据
        results.append(("15分钟数据", test_minute_data("600519", "15")))

        # 5. 财务数据
        results.append(("财务数据", test_financial_data("600519")))

        # 退出
        bs.logout()
    else:
        results.append(("登录", False))

    # 测试总结
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)

    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")

    all_passed = all(r[1] for r in results)
    print("\n" + "="*60)
    if all_passed:
        print("[成功] 所有测试通过！Baostock 可支持完整架构")
    else:
        print("[警告] 部分测试失败，请检查")
    print("="*60)

if __name__ == "__main__":
    main()
