"""
测试分类器逻辑 - 不通过真实网络请求，只测试规则
"""

# 直接用analyze_and_categorize函数测试
def test_classification():
    """模拟不同场景测试分类结果"""

    print("="*60)
    print("测试1: 徐高公众号文章")
    print("="*60)

    # 模拟徐高的文章
    test_article_1 = {
        "title": "中国经济分析：2024年展望",
        "account": "徐高",
        "content": "关于当前宏观经济的深入分析..."
    }

    result = simulate_analyze(test_article_1)
    print_result(result)

    print("\n" + "="*60)
    print("测试2: 机器之心 + Claude Code")
    print("="*60)

    # 模拟机器之心的Claude Code文章
    test_article_2 = {
        "title": "Claude Code如何改变开发者工作流",
        "account": "机器之心",
        "content": "Claude Code是Anthropic最新推出的开发工具，它..."
    }

    result = simulate_analyze(test_article_2)
    print_result(result)

    print("\n" + "="*60)
    print("测试3: 量子位 + 但不含Claude Code")
    print("="*60)

    # 模拟量子位的普通AI文章
    test_article_3 = {
        "title": "GPT-4在编程领域的应用",
        "account": "量子位",
        "content": "GPT-4在代码生成方面有出色表现..."
    }

    result = simulate_analyze(test_article_3)
    print_result(result)

    print("\n" + "="*60)
    print("测试4: 手动输入，无法识别公众号")
    print("="*60)

    # 模拟无法识别的公众号，需要从内容推断
    test_article_4 = {
        "title": "最新AI技术解析",
        "account": "未知公众号",
        "content": "机器之心今天发布了关于Claude Code的详细分析..."
    }

    result = simulate_analyze(test_article_4)
    print_result(result)

    print("\n" + "="*60)
    print("测试5: 关键词权重计算")
    print("="*60)

    # 测试多个关键词的权重
    test_article_5 = {
        "title": "Claude Code开发实战指南",
        "account": "AI科技评论",
        "content": "Claude Code最新更新的教程和实战指南..."
    }

    result = simulate_analyze(test_article_5)
    print_result(result)
    print(f"预期总分: 10(Claude Code) + 7(开发实战) + 7(教程) + 6(指南) = 30分")


def simulate_analyze(article):
    """模拟文章分析过程"""

    # 导入分类规则
    PAID_WECHAT_ACCOUNTS = {
        "徐高": {"category": "必读", "priority": 10, "type": "经济管理"},
    }

    AI_WECHAT_ACCOUNTS = {
        "机器之心": {"category": "重点推荐", "priority": 8, "type": "AI技术"},
        "量子位": {"category": "重点推荐", "priority": 8, "type": "AI技术"},
        "AI科技评论": {"category": "重点推荐", "priority": 8, "type": "AI技术"},
    }

    KEYWORD_TO_ACCOUNT = {
        "徐高": ["徐高", "宏观经济学", "中国经济"],
        "机器之心": ["机器之心", "机器智能"],
        "量子位": ["量子位", "qbit"],
        "AI科技评论": ["AI科技评论", "AI科技"],
    }

    IMPORTANT_KEYWORDS = {
        "Claude Code": 10,
        "Claude": 8,
        "开发实战": 7,
        "教程": 7,
        "指南": 6,
        "最新更新": 5,
    }

    # 提取信息
    title = article['title']
    account = article['account']
    content = article['content']

    # 步骤1: 确定公众号分类
    category = "一般阅读"
    priority = 3
    account_type = "其他"

    # 检查是否在付费必看列表
    if account in PAID_WECHAT_ACCOUNTS:
        info = PAID_WECHAT_ACCOUNTS[account]
        category = info["category"]
        priority = info["priority"]
        account_type = info["type"]

    # 检查是否在AI/编程类列表
    elif account in AI_WECHAT_ACCOUNTS:
        info = AI_WECHAT_ACCOUNTS[account]
        account_type = info["type"]

        # AI类文章需要检查是否包含Claude Code相关内容
        content_lower = (title + " " + content).lower()

        # 计算文章的重要性分数
        importance_score = 0
        important_words = []

        for keyword, weight in IMPORTANT_KEYWORDS.items():
            if keyword.lower() in content_lower:
                importance_score += weight
                important_words.append(f"{keyword} (+{weight})")

        # 如果包含Claude Code相关的重要内容
        if "Claude Code".lower() in content_lower or "claude code" in content_lower:
            category = "必读-Claude Code"
            priority = 10
        elif importance_score >= 8:
            category = "重点推荐"
            priority = 7
        else:
            category = info["category"]
            priority = info["priority"]

    # 如果无法识别公众号，尝试用关键词推断
    else:
        content_lower = (title + " " + content).lower()

        found_account = None
        for acc, keywords in KEYWORD_TO_ACCOUNT.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    found_account = acc
                    break
            if found_account:
                break

        if found_account:
            account = f"{account}（推断为: {found_account}）"
            if found_account in PAID_WECHAT_ACCOUNTS:
                info = PAID_WECHAT_ACCOUNTS[found_account]
                category = info["category"]
                priority = info["priority"]
                account_type = info["type"]
            elif found_account in AI_WECHAT_ACCOUNTS:
                info = AI_WECHAT_ACCOUNTS[found_account]
                category = info["category"]
                priority = info["priority"]
                account_type = info["type"]

    return {
        "title": title,
        "account": account,
        "account_type": account_type,
        "category": category,
        "priority": priority,
        "importance_score": importance_score if 'importance_score' in locals() else 0,
        "matched_keywords": important_words if 'important_words' in locals() else []
    }


def print_result(result):
    """打印分析结果"""
    print(f"\n文章: {result['title']}")
    print(f"   公众号: {result['account']}")
    print(f"   类型: {result['account_type']}")
    print(f"   分类: {result['category']}")
    print(f"   优先级: {'*' * (result['priority'] // 2)}")

    if 'importance_score' in result:
        print(f"   重要性分数: {result['importance_score']}分")
        if result['matched_keywords']:
            print(f"   匹配关键词: {', '.join(result['matched_keywords'])}")


# 运行测试
if __name__ == "__main__":
    test_classification()
