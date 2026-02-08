# -*- coding: utf-8 -*-
"""
调试 Baostock 数据下载问题
"""

import baostock as bs
from datetime import datetime, timedelta
import pandas as pd

def test_daily_download(symbol="600519"):
    """测试日线下载"""
    print(f"\n测试下载 {symbol} 日线数据")
    print("="*60)

    # 登录
    lg = bs.login()
    if lg.error_code != '0':
        print(f"登录失败: {lg.error_msg}")
        return
    print("登录成功")

    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=3*365)

        prefix = 'sh' if symbol.startswith('6') else 'sz'
        code = f"{prefix}.{symbol}"

        print(f"股票代码: {code}")
        print(f"开始日期: {start_date.strftime('%Y-%m-%d')}")
        print(f"结束日期: {end_date.strftime('%Y-%m-%d')}")

        # 尝试下载
        rs = bs.query_history_k_data_plus(
            code=code,
            fields='date,open,high,low,close,volume',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            frequency='d',
            adjustflag='3'
        )

        print(f"请求结果码: {rs.error_code}")
        print(f"请求错误信息: {rs.error_msg}")

        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())

        print(f"获取数据条数: {len(data_list)}")

        if data_list:
            df = pd.DataFrame(data_list, columns=rs.fields)
            print(f"\n前5条数据:")
            print(df.head())
        else:
            print("无数据返回")

    except Exception as e:
        print(f"异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    bs.logout()

if __name__ == "__main__":
    test_daily_download("600519")
