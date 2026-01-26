"""
微信公众号文章分类工具 v1.0
功能：通过微信公众号文章链接，自动分类并生成阅读优先级报告
"""

# 导入必要的工具箱
import re  # 正则表达式，用于在文本中查找模式（像用特殊的放大镜找关键词）


# ==================== 步骤1: 定义公众号分类规则 ====================
# 这就像你有三个书架：必读、重点推荐、一般阅读

PAID_WECHAT_ACCOUNTS = {
    "徐高": {"category": "必读", "priority": 10, "type": "经济管理"},
}

# AI/编程类公众号 - 需要检查是否有Claude Code相关内容
AI_WECHAT_ACCOUNTS = {
    "机器之心": {"category": "重点推荐", "priority": 8, "type": "AI技术"},
    "量子位": {"category": "重点推荐", "priority": 8, "type": "AI技术"},
    "AI科技评论": {"category": "重点推荐", "priority": 8, "type": "AI技术"},
    "新智元": {"category": "重点推荐", "priority": 8, "type": "AI技术"},
}

# 关键词到公众号的映射（当文章中没有明确公众号名时）
KEYWORD_TO_ACCOUNT = {
    "徐高": ["徐高", "宏观经济学", "中国经济"],
    "机器之心": ["机器之心", "机器智能"],
    "量子位": ["量子位", "量子位", "qbit"],
    "AI科技评论": ["AI科技评论", "AI科技", "AI Review"],
    "新智元": ["新智元", "AI纪元"],
}

# 判断文章重要性的关键词及权重
IMPORTANT_KEYWORDS = {
    "Claude Code": 10,      # 最重要的关键词
    "Claude": 8,            # 重要
    "开发实战": 7,          # 实操性强
    "教程": 7,              # 学习价值高
    "指南": 6,              # 参考性强
    "最新更新": 5,          # 时效性强
    "对比": 5,              # 分析类文章
    "解读": 5,              # 深度分析
    "实战": 6,              # 实践价值
}


# ==================== 步骤2: 获取文章内容（核心挑战） ====================
def fetch_article_content(url):
    """
    从微信文章链接获取内容
    挑战：微信公众号有反爬机制，可能无法直接访问

    返回: (文章标题, 文章内容, 公众号名称)
    """
    print(f"\n尝试获取文章: {url}")
    print("注意：由于微信反爬机制，直接访问可能受限...")

    # 这里我们需要写一个"贪心"的函数
    # 先尝试最佳方案，如果失败就提供备选方案

    # 方案A: 尝试直接请求（可能失败）
    try:
        import urllib.request  # 导入网络请求工具
        from urllib.error import URLError

        # 设置请求头，伪装成浏览器（避免被识别为爬虫）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)

        # 尝试获取网页内容
        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode('utf-8')

            # 从HTML中提取标题（用正则表达式像寻宝一样找）
            title_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
            title = title_match.group(1) if title_match else "无法获取标题"

            # 从HTML中提取公众号名称
            # 微信文章通常在<meta>标签或特定class中
            account_match = re.search(r'meta name="author" content="(.*?)"', html_content)
            if not account_match:
                account_match = re.search(r'var biz = "(.*?)"', html_content)

            account_name = account_match.group(1) if account_match else "未知公众号"

            # 提取正文内容（这部分最难）
            # 微信文章内容通常在rich_media_content中
            content_match = re.search(r'class="rich_media_content"[^>]*>(.*?)</div>',
                                     html_content, re.DOTALL)
            content = content_match.group(1) if content_match else "无法提取正文"

            # 清理HTML标签，只保留纯文本
            content = re.sub(r'<[^>]+>', '', content)  # 移除HTML标签
            content = re.sub(r'\s+', ' ', content)  # 合并多余空白

            return title, content.strip(), account_name

    except URLError as e:
        print(f"\n❌ 无法直接访问该链接: {e}")
        print("微信公众号有反爬机制，建议按住Ctrl键点击链接，在浏览器中打开后手动复制标题和第一段内容。\n")

        # 提供备用方案
        return None, None, None

    except Exception as e:
        print(f"\n❌ 获取文章时出错: {e}")
        return None, None, None


# ==================== 步骤3: 分析文章并分类 ====================
def analyze_and_categorize(url):
    """
    分析微信文章并返回分类结果
    """
    # 步骤1: 获取文章内容
    title, content, account_name = fetch_article_content(url)

    # 如果获取失败，提供手动输入模式
    if title is None:
        print("\n" + "="*50)
        print("备用方案：请手动输入文章信息")
        print("="*50)

        title = input("\n请输入文章标题: ")
        account_name = input("请输入公众号名称: ")
        content_preview = input("请输入文章第一段内容（用于判断主题）: ")
        content = content_preview

    # 步骤2: 确定公众号分类
    category = "一般阅读"
    priority = 3  # 默认优先级3（最低）
    account_type = "其他"

    # 检查是否在付费必看列表
    if account_name in PAID_WECHAT_ACCOUNTS:
        info = PAID_WECHAT_ACCOUNTS[account_name]
        category = info["category"]
        priority = info["priority"]
        account_type = info["type"]

    # 检查是否在AI/编程类列表
    elif account_name in AI_WECHAT_ACCOUNTS:
        info = AI_WECHAT_ACCOUNTS[account_name]
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

        for account, keywords in KEYWORD_TO_ACCOUNT.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    account_name = account  # 推断出公众号

                    # 重新进行分类
                    if account in PAID_WECHAT_ACCOUNTS:
                        info = PAID_WECHAT_ACCOUNTS[account]
                        category = info["category"]
                        priority = info["priority"]
                        account_type = info["type"]
                    elif account in AI_WECHAT_ACCOUNTS:
                        info = AI_WECHAT_ACCOUNTS[account]
                        category = info["category"]
                        priority = info["priority"]
                        account_type = info["type"]
                    break

    # 返回分析结果
    return {
        "url": url,
        "title": title,
        "account": account_name,
        "account_type": account_type,
        "category": category,
        "priority": priority,
        "word_count": len(content) if content else 0,
    }


# ==================== 步骤4: 生成分类报告 ====================
def generate_report(articles):
    """
    生成分类后的阅读清单报告
    """
    print("\n" + "="*60)
    print("📊 微信公众号文章分类报告")
    print("="*60)

    # 按优先级排序（高→低）
    articles_sorted = sorted(articles, key=lambda x: x["priority"], reverse=True)

    current_category = ""
    for article in articles_sorted:
        # 分类换行
        if article["category"] != current_category:
            current_category = article["category"]
            print(f"\n{'='*60}")
            print(f"🔖 {current_category}")
            print(f"{'='*60}")

        # 显示文章信息
        print(f"\n📰 {article['title']}")
        print(f"   公众号: {article['account']} ({article['account_type']})")
        print(f"   链接: {article['url']}")
        if article['word_count'] > 0:
            print(f"   字数: {article['word_count']}字")
        print(f"   优先级: {'⭐' * (article['priority'] // 2)}")

    # 统计信息
    print("\n" + "="*60)
    print("📈 阅读统计")
    print("="*60)
    total = len(articles)
    must_read = len([a for a in articles if a["priority"] >= 8])
    important = len([a for a in articles if a["priority"] >= 5])

    print(f"总计: {total}篇文章")
    print(f"必读（⭐⭐⭐⭐⭐）: {must_read}篇")
    print(f"重点推荐（⭐⭐⭐⭐）: {important - must_read}篇")


# ==================== 主程序入口 ====================
def main():
    """
    主程序：循环输入文章链接，生成分类报告
    """
    print("="*60)
    print("📚 微信公众号文章分类工具 v1.0")
    print("="*60)
    print("""
使用说明：
1. 复制微信文章的链接（在微信中，点击右上角...，选择"复制链接"）
2. 在程序中粘贴链接
3. 输入"结束"来生成报告

注意：由于微信反爬机制，可能无法直接获取部分文章内容。
如果失败，请手动输入标题、公众号和正文预览。
""")

    articles = []  # 存放所有文章的列表

    while True:
        print("\n" + "-"*60)
        url = input('\n请输入微信文章链接（或输入"结束"）: ').strip()

        if url.lower() in ["结束", "quit", "exit", "done"]:
            if articles:
                generate_report(articles)
            else:
                print("\n❌ 未添加任何文章")
            break

        if not url:
            print("❌ 链接不能为空")
            continue

        if not url.startswith("http"):
            print("❌ 请输入有效的URL链接（以http://或https://开头）")
            continue

        # 分析文章
        try:
            result = analyze_and_categorize(url)
            articles.append(result)
            print(f"\n✅ 已添加: {result['title'][:50]}...")
            print(f"   分类: {result['category']}")
            print(f"   公众号: {result['account']}")
        except Exception as e:
            print(f"\n❌ 处理出错: {e}")


# 当这个文件直接运行时，执行main()函数
if __name__ == "__main__":
    main()
