# -*- coding: utf-8 -*-
"""
测试财务数据下载功能
"""

from data_manager import BaostockDownloader, DatabaseManager

def test_financial_data(symbol="600519"):
    """测试单只股票财务数据下载"""
    print("="*60)
    print(f"测试下载 {symbol} 财务数据")
    print("="*60)

    db = DatabaseManager()
    downloader = BaostockDownloader(db)

    # 测试下载 - 捕获完整异常
    try:
        result = downloader.download_financial_data(symbol)
    except Exception as e:
        print(f"\n详细错误信息:")
        import traceback
        traceback.print_exc()
        result = False

    print("\n" + "="*60)
    if result:
        print("✓ 财务数据下载成功")

        # 验证数据
        data = db.get_financial_data(symbol)
        print(f"\n验证数据:")
        print(f"  - 财务摘要: {len(data.get('abstract', []))} 条")
        print(f"  - 资产负债表: {len(data.get('balance_sheet', []))} 条")
        print(f"  - 利润表: {len(data.get('income_statement', []))} 条")
        print(f"  - 现金流量表: {len(data.get('cash_flow', []))} 条")
    else:
        print("✗ 财务数据下载失败")

    print("="*60)

if __name__ == "__main__":
    import sys
    symbol = sys.argv[1] if len(sys.argv) > 1 else "600519"
    test_financial_data(symbol)
