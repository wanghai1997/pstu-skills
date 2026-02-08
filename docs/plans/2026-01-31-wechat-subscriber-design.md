# 微信文章订阅器 - 设计文档

**项目名称:** wechat-subscriber
**设计日期:** 2026-01-31
**版本:** 1.0

---

## 1. 项目概述

### 1.1 背景
基于现有的 `wechat-article-downloader` skill，构建一个自动化订阅系统，实现对多个微信公众号文章的定期检查和自动下载。

### 1.2 目标用户
- 订阅大量公众号（50+）的用户
- 希望手动控制运行时机（非后台常驻）
- 需要统一管理下载的文章

### 1.3 核心需求
| 需求 | 说明 |
|------|------|
| 批量订阅管理 | 支持50+公众号的配置管理 |
| 手动触发检查 | 用户手动运行，发现新文章 |
| URL去重 | 已下载的文章不再重复下载 |
| 统一存储 | 所有PDF放入同一文件夹 |
| 短文件名 | 文件名为 article_XXXX.pdf |
| 详细记录 | 记录文章URL、标题、作者、发布时间等 |
| 并发检查 | 同时检查5个公众号，加快速度 |
| 生成报告 | HTML格式报告，按公众号分组 |
| 数据备份 | 支持配置和数据的导出/导入 |

---

## 2. 系统架构

### 2.1 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                     用户交互层 (CLI)                         │
│  python subscriber.py run      # 检查新文章                  │
│  python subscriber.py list     # 查看订阅列表                │
│  python subscriber.py add      # 添加订阅                    │
│  python subscriber.py remove   # 删除订阅                    │
│  python subscriber.py stats    # 查看统计                    │
│  python subscriber.py backup   # 数据备份                    │
│  python subscriber.py restore  # 数据恢复                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     核心控制层 (Scheduler)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ 订阅管理器  │  │ 任务调度器  │  │  文章变更检测器     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     数据处理层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ 网页抓取器  │  │ 文章下载器  │  │  内容解析器         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     数据存储层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ 订阅列表    │  │ 文章数据库  │  │  下载目录           │  │
│  │ (JSON)      │  │ (SQLite)    │  │  (PDF/Markdown)     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 模块职责

| 模块 | 职责 |
|------|------|
| ConfigManager | 管理订阅配置（增删改查、导入导出） |
| ArticleDatabase | 管理文章元数据（SQLite操作） |
| WeChatSpider | 抓取公众号文章列表（5并发） |
| ArticleDownloader | 下载文章为PDF（复用现有代码） |
| ReportGenerator | 生成HTML运行报告 |
| WeChatSubscriber | 主控制器，协调各模块 |

---

## 3. 数据存储设计

### 3.1 目录结构

```
wechat-subscriber/                    # 项目目录
├── config/
│   └── subscriptions.json            # 订阅列表（50+公众号）
├── data/
│   └── articles.db                   # SQLite数据库
├── downloads/                        # 所有PDF
│   ├── article_0001.pdf
│   ├── article_0002.pdf
│   └── ...
├── reports/                          # 运行报告
│   ├── 2026-01-31_14-30-00.html
│   └── 2026-01-30_09-15-00.html
└── subscriber.py                     # 主程序
```

### 3.2 订阅列表 (subscriptions.json)

```json
{
  "settings": {
    "download_dir": "./downloads",
    "report_dir": "./reports",
    "concurrent_workers": 5,
    "request_timeout": 30
  },
  "subscriptions": [
    {
      "id": "sub_001",
      "name": "机器之心",
      "history_url": "https://mp.weixin.qq.com/mp/profile?src=...",
      "category": "AI",
      "added_at": "2026-01-15"
    }
  ]
}
```

### 3.3 数据库表结构

```sql
-- 文章表
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT,              -- 如: article_0001.pdf
    url TEXT UNIQUE,             -- 文章URL（去重依据）
    title TEXT,                  -- 文章标题
    author TEXT,                 -- 公众号名称
    publish_date TEXT,           -- 发布时间
    download_date TEXT,          -- 下载时间
    file_path TEXT,              -- 文件完整路径
    file_size INTEGER            -- 文件大小（字节）
);

-- 运行记录表
CREATE TABLE runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_time TEXT,               -- 运行时间
    checked_count INTEGER,       -- 检查了多少个公众号
    new_found INTEGER,           -- 发现多少篇新文章
    downloaded INTEGER,          -- 成功下载多少篇
    failed INTEGER,              -- 失败多少篇
    report_path TEXT             -- 报告文件路径
);
```

---

## 4. 核心模块设计

### 4.1 ConfigManager

```python
class ConfigManager:
    """订阅配置管理器"""

    def load_subscriptions(self) -> List[Subscription]:
        """加载所有订阅"""

    def add_subscription(self, name: str, url: str, category: str = "") -> bool:
        """添加新订阅"""

    def remove_subscription(self, sub_id: str) -> bool:
        """删除订阅"""

    def export_config(self, output_path: str):
        """导出配置（备份）"""

    def import_config(self, input_path: str):
        """导入配置（恢复）"""
```

### 4.2 ArticleDatabase

```python
class ArticleDatabase:
    """文章数据库"""

    def is_article_exists(self, url: str) -> bool:
        """检查文章是否已下载（URL去重）"""

    def add_article(self, article: Article) -> int:
        """添加文章记录，返回文章编号"""

    def get_article_by_id(self, article_id: int) -> Article:
        """根据编号获取文章信息"""

    def export_data(self, output_path: str):
        """导出所有数据（备份）"""

    def import_data(self, input_path: str):
        """导入数据（恢复）"""
```

### 4.3 WeChatSpider

```python
class WeChatSpider:
    """微信文章抓取器"""

    def __init__(self, max_workers: int = 5):
        """初始化，设置并发数"""

    def fetch_articles(self, subscription: Subscription) -> List[Article]:
        """获取单个公众号的最新文章列表"""

    def fetch_all(self, subscriptions: List[Subscription]) -> Dict[str, List[Article]]:
        """并发获取所有公众号的文章（5并发）"""
```

### 4.4 ArticleDownloader

```python
class ArticleDownloader:
    """文章下载器"""

    def download(self, article: Article, output_dir: str) -> DownloadResult:
        """
        下载单篇文章
        - 复用现有 wechat-article-downloader 代码
        - 生成短文件名 article_XXXX.pdf
        - 失败时记录原因，不重试
        """
```

### 4.5 ReportGenerator

```python
class ReportGenerator:
    """报告生成器"""

    def generate(self, run_result: RunResult, output_dir: str) -> str:
        """
        生成HTML报告
        - 按公众号分组显示
        - 包含文章标题、作者、发布时间
        - 可点击打开PDF
        - 显示失败的公众号
        """
```

### 4.6 WeChatSubscriber（主控制器）

```python
class WeChatSubscriber:
    """微信订阅主程序"""

    def __init__(self):
        self.config = ConfigManager()
        self.db = ArticleDatabase()
        self.spider = WeChatSpider(max_workers=5)
        self.downloader = ArticleDownloader()
        self.reporter = ReportGenerator()

    def run(self) -> RunResult:
        """
        主流程：
        1. 加载订阅列表
        2. 并发抓取所有公众号文章（5并发）
        3. 检查哪些是新文章（URL去重）
        4. 下载新文章（失败不重试，记录即可）
        5. 生成HTML报告（按公众号分组）
        6. 记录运行日志
        """
```

---

## 5. CLI命令设计

### 5.1 命令列表

| 命令 | 功能 | 示例 |
|------|------|------|
| `run` | 检查所有订阅，下载新文章 | `python subscriber.py run` |
| `list` | 查看所有订阅 | `python subscriber.py list` |
| `add` | 添加新订阅 | `python subscriber.py add "机器之心" "https://..."` |
| `remove` | 删除订阅 | `python subscriber.py remove sub_001` |
| `stats` | 查看统计信息 | `python subscriber.py stats` |
| `backup` | 备份数据 | `python subscriber.py backup` |
| `restore` | 恢复数据 | `python subscriber.py restore backup.zip` |

### 5.2 运行示例

```bash
# 检查新文章
$ python subscriber.py run
[INFO] 正在检查 52 个公众号...
[INFO] 机器之心: 发现 3 篇新文章
[INFO] 量子位: 发现 1 篇新文章
[INFO] 正在下载 4 篇文章...
[SUCCESS] 下载完成: 4 篇成功, 0 篇失败
[INFO] 报告已生成: reports/2026-01-31_14-30-00.html

# 查看订阅列表
$ python subscriber.py list
当前订阅 52 个公众号：
┌──────┬─────────┬──────────┬────────────┐
│ 编号 │ 名称    │ 分类     │ 添加日期   │
├──────┼─────────┼──────────┼────────────┤
│ 1    │ 机器之心 │ AI       │ 2026-01-15 │
│ 2    │ 量子位   │ AI       │ 2026-01-16 │
│ ...  │ ...     │ ...      │ ...        │
└──────┴─────────┴──────────┴────────────┘

# 查看统计
$ python subscriber.py stats
============ 订阅统计 ============
订阅公众号数: 52
已下载文章数: 1,247
本次运行发现: 4 篇新文章
上次运行时间: 2026-01-30 09:15:00
```

---

## 6. 报告格式

### 6.1 HTML报告内容

- **运行摘要**: 检查公众号数、发现新文章数、成功/失败数
- **新文章列表**: 按公众号分组
  - 公众号名称
  - 文章列表（标题、发布时间、文件链接）
- **失败记录**: 抓取失败的公众号及错误原因
- **运行时间**: 开始时间、耗时

---

## 7. 技术选型

| 组件 | 选型 | 原因 |
|------|------|------|
| 配置存储 | JSON | 易于手动编辑，人类可读 |
| 数据存储 | SQLite | 轻量，无需单独服务器 |
| 并发处理 | ThreadPoolExecutor | 标准库，简单易用 |
| HTML生成 | Jinja2 | 模板引擎，生成美观报告 |
| 下载逻辑 | 复用现有代码 | 保持兼容性 |

---

## 8. 待办事项

- [ ] 创建项目目录结构
- [ ] 实现 ConfigManager 模块
- [ ] 实现 ArticleDatabase 模块
- [ ] 实现 WeChatSpider 模块
- [ ] 实现 ArticleDownloader 模块
- [ ] 实现 ReportGenerator 模块
- [ ] 实现 CLI 主程序
- [ ] 编写测试用例
- [ ] 编写使用文档

---

## 9. 设计决策记录

### 决策1: 选择方案2（链接轮询）而非模拟登录
**原因**: 微信反爬严格，模拟登录容易封号。链接轮询更稳定可控。

### 决策2: 短文件名（article_XXXX.pdf）而非长文件名
**原因**: 用户选择D，简单管理，详细信息在数据库中查询。

### 决策3: 手动触发而非定时任务
**原因**: 用户选择A，手动控制运行时机，避免后台常驻。

### 决策4: URL去重而非标题去重
**原因**: 用户选择A，简单可靠，同一URL确保是同一篇文章。

### 决策5: 5并发而非顺序检查
**原因**: 用户选择B，平衡速度和稳定性，避免被微信限制。

### 决策6: 失败不重试
**原因**: 用户选择A，记录即可，下次运行再处理。

### 决策7: HTML报告按公众号分组
**原因**: 用户选择C，便于按来源查看文章。

---

**文档版本:** 1.0
**最后更新:** 2026-01-31
**设计状态:** 已完成，待实现
