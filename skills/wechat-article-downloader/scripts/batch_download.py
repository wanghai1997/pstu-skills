#!/usr/bin/env python3
"""
批量下载微信公众号文章
支持从JSON或CSV文件批量下载文章
"""

import sys
import json
import csv
import time
from pathlib import Path
from typing import List, Dict, Any

# 导入单个文章下载功能
try:
    from download_article import WeChatArticleDownloader
except ImportError:
    print("错误: 找不到 download_article.py")
    sys.exit(1)


def read_article_list(file_path: str) -> List[Dict[str, Any]]:
    """
    从文件读取文章列表

    支持格式:
    - JSON: [{"url": "...", "title": "..."}, ...]
    - CSV: url,title

    Args:
        file_path: 输入文件路径

    Returns:
        文章列表
    """
    articles = []
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"错误: 文件不存在: {file_path}")
        return []

    # 根据文件扩展名选择读取方法
    if file_path.suffix.lower() == '.json':
        articles = read_json_file(file_path)
    elif file_path.suffix.lower() in ['.csv', '.txt']:
        articles = read_csv_file(file_path)
    else:
        print(f"错误: 不支持的文件格式: {file_path.suffix}")
        return []

    return articles


def read_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """读取JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 验证数据结构
        if isinstance(data, list):
            articles = []
            for item in data:
                if isinstance(item, dict) and 'url' in item:
                    articles.append({
                        'url': item['url'],
                        'title': item.get('title', ''),
                        'tags': item.get('tags', [])
                    })
            return articles
        else:
            print("错误: JSON文件应该是列表格式")
            return []

    except json.JSONDecodeError as e:
        print(f"错误: JSON文件格式错误: {str(e)}")
        return []
    except Exception as e:
        print(f"错误: 读取JSON文件失败: {str(e)}")
        return []


def read_csv_file(file_path: Path) -> List[Dict[str, Any]]:
    """读取CSV文件"""
    try:
        articles = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            # 检查必需的列
            if 'url' not in reader.fieldnames:
                print("错误: CSV文件需要包含 'url' 列")
                return []

            for row in reader:
                articles.append({
                    'url': row['url'],
                    'title': row.get('title', ''),
                    'tags': row.get('tags', '').split(',') if row.get('tags') else []
                })

        return articles

    except Exception as e:
        print(f"错误: 读取CSV文件失败: {str(e)}")
        return []


def batch_download(articles: List[Dict[str, Any]], output_dir: str,
                   include_images: bool = True, timeout: int = 30,
                   delay: float = 1.0) -> List[Dict[str, Any]]:
    """
    批量下载文章

    Args:
        articles: 文章列表
        output_dir: 输出目录
        include_images: 是否包含图片
        timeout: 请求超时时间
        delay: 请求间隔（秒）

    Returns:
        下载结果列表
    """
    results = []
    total = len(articles)

    if total == 0:
        print("没有文章需要下载")
        return results

    print(f"开始批量下载 {total} 篇文章\n")

    # 创建下载器
    downloader = WeChatArticleDownloader(
        timeout=timeout,
        include_images=include_images
    )

    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 下载每篇文章
    for i, article in enumerate(articles, 1):
        url = article.get('url', '')
        title = article.get('title', '')

        print(f"[{i}/{total}] 下载: {title or url}")

        # 检查URL是否有效
        if not url or not ("weixin.qq.com" in url or "mp.weixin.qq.com" in url):
            print(f"  ✗ 无效的URL: {url}\n")
            results.append({
                'url': url,
                'title': title,
                'status': 'failed',
                'error': 'Invalid URL'
            })
            continue

        try:
            # 下载文章
            article_data = downloader.fetch_article_content(url)

            if article_data:
                # 生成文件名
                if title:
                    safe_name = re.sub(r'[^\w\s-]', '', title)
                    filename = safe_name.strip().replace(' ', '_')
                else:
                    filename = None

                # 保存文章
                saved_path = downloader.save_article_data(
                    article_data,
                    output_dir,
                    filename
                )

                print(f"  ✓ 成功\n")
                results.append({
                    'url': url,
                    'title': title,
                    'status': 'success',
                    'saved_path': saved_path
                })
            else:
                print(f"  ✗ 失败\n")
                results.append({
                    'url': url,
                    'title': title,
                    'status': 'failed',
                    'error': 'Download failed'
                })

        except Exception as e:
            print(f"  ✗ 错误: {str(e)}\n")
            results.append({
                'url': url,
                'title': title,
                'status': 'failed',
                'error': str(e)
            })

        # 添加延迟以避免请求过快
        if i < total:
            time.sleep(delay)

    return results


def save_download_report(results: List[Dict[str, Any]], output_path: str):
    """保存下载报告"""
    report = {
        'summary': {
            'total': len(results),
            'successful': len([r for r in results if r['status'] == 'success']),
            'failed': len([r for r in results if r['status'] == 'failed'])
        },
        'details': results
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def print_usage():
    """打印使用说明"""
    print("""
批量下载微信公众号文章

用法:
  python batch_download.py <文章列表文件> [选项]

文章列表文件格式:
  - JSON: [{"url": "...", "title": "..."}, ...]
  - CSV: url,title

选项:
  --output-dir PATH    输出目录 (默认: ./downloads)
  --no-images          不包含图片 (默认: 包含图片)
  --timeout SECONDS    请求超时时间 (默认: 30秒)
  --delay SECONDS      请求间隔时间 (默认: 1.0秒)
  --report PATH        生成下载报告到指定文件

示例:
  # 从JSON文件批量下载
  python batch_download.py articles.json

  # 指定输出目录和超时时间
  python batch_download.py articles.json \
    --output-dir ./my_articles \
    --timeout 60

  # 不包含图片，添加2秒间隔
  python batch_download.py articles.json \
    --no-images --delay 2.0

  # 生成下载报告
  python batch_download.py articles.json \
    --report ./download_report.json
    """)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    input_file = sys.argv[1]

    # 默认参数
    output_dir = "./downloads"
    include_images = True
    timeout = 30
    delay = 1.0
    report_path = None

    # 解析命令行参数
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == "--output-dir" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        elif arg == "--no-images":
            include_images = False
            i += 1
        elif arg == "--timeout" and i + 1 < len(sys.argv):
            timeout = int(sys.argv[i + 1])
            i += 2
        elif arg == "--delay" and i + 1 < len(sys.argv):
            delay = float(sys.argv[i + 1])
            i += 2
        elif arg == "--report" and i + 1 < len(sys.argv):
            report_path = sys.argv[i + 1]
            i += 2
        else:
            print(f"警告: 未知参数: {arg}")
            i += 1

    try:
        # 读取文章列表
        print(f"正在读取文章列表: {input_file}\n")
        articles = read_article_list(input_file)

        if not articles:
            print("没有有效的文章需要下载")
            sys.exit(1)

        print(f"找到 {len(articles)} 篇文章\n")

        # 批量下载
        results = batch_download(
            articles=articles,
            output_dir=output_dir,
            include_images=include_images,
            timeout=timeout,
            delay=delay
        )

        # 打印汇总
        successful = len([r for r in results if r['status'] == 'success'])
        failed = len([r for r in results if r['status'] == 'failed'])

        print("=" * 50)
        print("下载完成!")
        print(f"总计: {len(results)} 篇")
        print(f"成功: {successful} 篇")
        print(f"失败: {failed} 篇")
        print("=" * 50)

        # 保存下载报告
        if report_path:
            save_download_report(results, report_path)
            print(f"\n下载报告已保存到: {report_path}")
        else:
            # 默认保存报告到输出目录
            default_report = Path(output_dir) / "download_report.json"
            save_download_report(results, str(default_report))
            print(f"\n下载报告已保存到: {default_report}")

        # 打印失败的详情
        if failed > 0:
            print("\n失败的下载:")
            for result in results:
                if result['status'] == 'failed':
                    print(f"  - {result.get('title', '未知标题')}")
                    print(f"    URL: {result.get('url', '')}")
                    print(f"    错误: {result.get('error', '未知错误')}")

    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import re  # 在文件顶部导入会更好，但这里为了代码完整性放在这里
    main()
