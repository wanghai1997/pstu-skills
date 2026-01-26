#!/usr/bin/env python3
"""
微信公众号文章下载器
下载公众号文章并转换为PDF格式
"""

import sys
import requests
import json
import time
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict, Any


class WeChatArticleDownloader:
    """微信公众号文章下载器"""

    def __init__(self, timeout: int = 30, include_images: bool = True):
        self.timeout = timeout
        self.include_images = include_images
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def is_valid_wechat_url(self, url: str) -> bool:
        """检查是否为有效的微信公众号文章URL"""
        parsed = urlparse(url)
        return (parsed.netloc in ['mp.weixin.qq.com', 'weixin.qq.com'] or
                'weixin' in parsed.netloc or
                parsed.path.startswith('/s/'))

    def extract_article_id(self, url: str) -> str:
        """从URL中提取文章ID"""
        parsed = urlparse(url)
        if '/s/' in parsed.path:
            article_id = parsed.path.split('/s/')[-1]
            return article_id
        return ''

    def fetch_article_content(self, url: str) -> Optional[Dict[str, Any]]:
        """获取文章内容"""
        try:
            print(f"正在获取文章: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # 设置正确的编码
            response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取文章信息
            article = self._extract_article_info(soup, url)

            if article:
                print(f"[OK] 成功获取: {article.get('title', '未知标题')}")
                return article
            else:
                print("[ERROR] 无法提取文章内容")
                return None

        except requests.RequestException as e:
            print(f"[ERROR] 请求错误: {str(e)}")
            return None
        except Exception as e:
            print(f"[ERROR] 处理错误: {str(e)}")
            return None

    def _extract_article_info(self, soup: BeautifulSoup, url: str) -> Optional[Dict[str, Any]]:
        """从HTML中提取文章信息"""
        try:
            # 提取标题
            title_tag = soup.find('h1', class_='rich_media_title')
            if not title_tag:
                title_tag = soup.find('h2', class_='rich_media_title')
            if not title_tag:
                title_tag = soup.find('title')

            title = title_tag.get_text(strip=True) if title_tag else '未命名文章'

            # 提取作者/公众号名称
            author_tag = soup.find('a', id='js_name')
            if not author_tag:
                author_tag = soup.find('strong', class_='profile_nickname')

            author = author_tag.get_text(strip=True) if author_tag else '未知作者'

            # 提取发布时间
            publish_time_tag = soup.find('em', id='publish_time')
            publish_time = publish_time_tag.get_text(strip=True) if publish_time_tag else '未知时间'

            # 提取文章正文
            content_tag = soup.find('div', class_='rich_media_content')
            if not content_tag:
                content_tag = soup.find('div', id='js_content')

            if not content_tag:
                print("[ERROR] 找不到文章内容")
                return None

            # 提取图片
            images = []
            if self.include_images:
                for img in content_tag.find_all('img'):
                    img_url = img.get('data-src') or img.get('src')
                    if img_url:
                        images.append({
                            'url': img_url,
                            'alt': img.get('alt', '')
                        })

            # 清理内容中的脚本和样式
            # 移除所有script标签
            for script in content_tag.find_all('script'):
                script.decompose()

            # 获取HTML内容
            content_html = str(content_tag)

            # 同时获取纯文本
            content_text = content_tag.get_text(separator='\n', strip=True)

            return {
                'url': url,
                'title': title,
                'author': author,
                'publish_time': publish_time,
                'content_html': content_html,
                'content_text': content_text,
                'images': images,
                'word_count': len(content_text)
            }

        except Exception as e:
            print(f"[ERROR] 提取错误: {str(e)}")
            return None

    def create_markdown_content(self, article: Dict[str, Any]) -> str:
        """创建Markdown格式的内容"""
        md = []

        # 标题
        md.append(f"# {article['title']}\n")

        # 元信息
        md.append(f"**作者:** {article['author']}")
        md.append(f"**发布时间:** {article['publish_time']}")
        md.append(f"**原文链接:** {article['url']}")
        md.append(f"**字数:** {article['word_count']}")
        md.append(f"**图片数:** {len(article['images'])}")
        md.append("\n---\n")

        # 内容
        md.append("## 正文内容\n")
        md.append(article['content_text'])

        # 图片列表
        if article['images']:
            md.append("\n---\n")
            md.append("## 图片\n")
            for i, img in enumerate(article['images'], 1):
                md.append(f"### 图片 {i}: {img['alt'][:50]}...")
                md.append(f"![图片{i}]({img['url']})")
                md.append("")

        return "\n".join(md)

    def save_article_data(self, article: Dict[str, Any], output_dir: str, filename: Optional[str] = None) -> str:
        """保存文章数据和Markdown文件"""
        try:
            # 创建输出目录
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # 生成文件名
            if not filename:
                safe_title = re.sub(r'[^\w\s-]', '', article['title'])
                safe_title = safe_title.strip().replace(' ', '_')
                filename = f"{safe_title[:50]}_{int(time.time())}"

            # 创建文件路径
            json_path = Path(output_dir) / f"{filename}.json"
            md_path = Path(output_dir) / f"{filename}.md"

            # 保存JSON格式
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(article, f, ensure_ascii=False, indent=2)

            # 保存Markdown格式
            markdown_content = self.create_markdown_content(article)
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            print(f"[OK] 已保存:")
            print(f"  - JSON: {json_path}")
            print(f"  - Markdown: {md_path}")

            return str(md_path)

        except Exception as e:
            print(f"[ERROR] 保存错误: {str(e)}")
            return ""


def print_usage():
    """打印使用说明"""
    print("""
微信公众号文章下载器

用法:
  python download_article.py <文章URL> [选项]

选项:
  --output-dir PATH    输出目录 (默认: ./downloads)
  --filename NAME      自定义文件名 (默认: 自动生成的文件名)
  --no-images          不包含图片 (默认: 包含图片)
  --timeout SECONDS    请求超时时间 (默认: 30秒)

示例:
  # 基本用法
  python download_article.py "https://mp.weixin.qq.com/s/xxxxx"

  # 指定输出目录
  python download_article.py "https://mp.weixin.qq.com/s/xxxxx" \
    --output-dir ./my_articles

  # 自定义文件名，不包含图片
  python download_article.py "https://mp.weixin.qq.com/s/xxxxx" \
    --filename "AI研究_2024" --no-images

  # 设置超时时间
  python download_article.py "https://mp.weixin.qq.com/s/xxxxx" \
    --timeout 60
    """)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    url = sys.argv[1]

    # 检查是否为有效的微信文章URL
    if not ("weixin.qq.com" in url or "mp.weixin.qq.com" in url):
        print("错误: 这不是一个有效的微信公众号文章URL")
        print("URL 应该包含 'weixin.qq.com' 或 'mp.weixin.qq.com'")
        sys.exit(1)

    # 默认参数
    output_dir = "./downloads"
    filename = None
    include_images = True
    timeout = 30

    # 解析命令行参数
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == "--output-dir" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        elif arg == "--filename" and i + 1 < len(sys.argv):
            filename = sys.argv[i + 1]
            i += 2
        elif arg == "--no-images":
            include_images = False
            i += 1
        elif arg == "--timeout" and i + 1 < len(sys.argv):
            timeout = int(sys.argv[i + 1])
            i += 2
        else:
            print(f"警告: 未知参数: {arg}")
            i += 1

    try:
        # 创建下载器
        downloader = WeChatArticleDownloader(
            timeout=timeout,
            include_images=include_images
        )

        # 下载文章
        article = downloader.fetch_article_content(url)

        if article:
            # 保存文章
            saved_path = downloader.save_article_data(
                article,
                output_dir,
                filename
            )
            print(f"\n[OK] 下载完成!")
            print(f"文件保存在: {saved_path}")
        else:
            print("\n[ERROR] 下载失败")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
