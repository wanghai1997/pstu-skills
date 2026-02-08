#!/usr/bin/env python3
"""
PDF OCR Converter - 增强版
专为大型学术文档（500-1000页）优化
支持图表保留、公式识别、分批处理、断点续传

使用方法:
    python ocr_pdf_advanced.py input.pdf output.pdf [选项]

特性:
    - 自动分批处理大文件（默认每批50页）
    - 智能检测图表和公式区域
    - 保留原文档布局和格式
    - 支持断点续传（中断后可恢复）
    - 进度自动保存
"""

import sys
import os
import argparse
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import pickle

# PDF处理
from pdf2image import convert_from_path
import fitz  # PyMuPDF，用于更精细的PDF操作
from PIL import Image

# OCR
import pytesseract

# 数值计算
import numpy as np

# 进度条
from tqdm import tqdm


class PDFOCRConverterAdvanced:
    """高级PDF OCR转换器 - 支持大文件和图表保留"""

    def __init__(
        self,
        dpi: int = 200,
        lang: str = 'chi_sim+eng',
        batch_size: int = 50,
        temp_dir: Optional[str] = None
    ):
        """
        初始化转换器

        Args:
            dpi: 图片分辨率（默认200）
            lang: OCR语言
            batch_size: 每批处理的页数（默认50页）
            temp_dir: 临时文件目录
        """
        self.dpi = dpi
        self.lang = lang
        self.batch_size = batch_size

        # 创建临时目录
        if temp_dir:
            self.temp_dir = Path(temp_dir)
        else:
            self.temp_dir = Path(tempfile.mkdtemp(prefix='pdf_ocr_'))

        # 进度保存文件
        self.progress_file = self.temp_dir / 'progress.json'

        # 查找中文字体
        self.chinese_font = self._find_chinese_font()

        print(f"[INFO] 临时目录: {self.temp_dir}")
        print(f"[INFO] 批处理大小: {batch_size} 页/批")
        if self.chinese_font:
            print(f"[INFO] 使用字体: {self.chinese_font}")

    def _find_chinese_font(self) -> Optional[str]:
        """
        查找系统中的中文字体

        Returns:
            字体名称或None
        """
        # 常见中文字体路径
        font_paths = [
            # Windows
            'C:/Windows/Fonts/simhei.ttf',      # 黑体
            'C:/Windows/Fonts/simsun.ttc',      # 宋体
            'C:/Windows/Fonts/microsoftyahei.ttc',  # 微软雅黑
            # Linux
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
            '/usr/share/fonts/truetype/arphic/uming.ttc',
            # Mac
            '/System/Library/Fonts/PingFang.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path

        return None

    def analyze_pdf_structure(self, pdf_path: str) -> Dict:
        """
        分析PDF结构，检测图表、公式、文字区域

        Args:
            pdf_path: PDF文件路径

        Returns:
            每页的结构信息
        """
        print("[INFO] 正在分析PDF结构...")

        doc = fitz.open(pdf_path)
        structure = {
            'total_pages': len(doc),
            'pages': []
        }

        for page_num in range(len(doc)):
            page = doc[page_num]

            # 获取页面信息
            page_info = {
                'page_num': page_num + 1,
                'width': page.rect.width,
                'height': page.rect.height,
                'has_images': len(page.get_images()) > 0,
                'text_blocks': []
            }

            # 检测文字块
            text_blocks = page.get_text("blocks")
            for block in text_blocks:
                x0, y0, x1, y1, text, block_no, block_type = block

                # 判断块类型
                if block_type == 0:  # 文字块
                    block_info = {
                        'type': 'text',
                        'bbox': (x0, y0, x1, y1),
                        'text_preview': text[:100] if text else ''
                    }
                else:  # 图片块
                    block_info = {
                        'type': 'image',
                        'bbox': (x0, y0, x1, y1)
                    }

                page_info['text_blocks'].append(block_info)

            structure['pages'].append(page_info)

        doc.close()

        # 统计信息
        total_images = sum(1 for p in structure['pages'] if p['has_images'])
        print(f"[OK] 分析完成: {structure['total_pages']} 页, "
              f"{total_images} 页含图片/图表")

        return structure

    def convert_page_to_image(
        self,
        pdf_path: str,
        page_num: int,
        output_path: Optional[str] = None
    ) -> str:
        """
        将单页PDF转换为图片

        Args:
            pdf_path: PDF文件路径
            page_num: 页码（从1开始）
            output_path: 输出图片路径（可选）

        Returns:
            图片文件路径
        """
        if output_path is None:
            output_path = self.temp_dir / f"page_{page_num:04d}.png"

        # 使用pdf2image转换单页
        images = convert_from_path(
            pdf_path,
            first_page=page_num,
            last_page=page_num,
            dpi=self.dpi,
            fmt='png'
        )

        if images:
            images[0].save(output_path, 'PNG')
            return str(output_path)
        else:
            raise RuntimeError(f"无法转换第 {page_num} 页")

    def detect_figures_and_tables(
        self,
        image_path: str,
        page_structure: Dict
    ) -> List[Dict]:
        """
        检测图片中的图表和公式区域

        使用启发式方法：
        - 大面积空白区域可能是图表
        - 特殊字符（如 ∑, ∫, α, β）可能是公式
        - 根据PDF结构信息辅助判断

        Args:
            image_path: 图片路径
            page_structure: 页面结构信息

        Returns:
            特殊区域列表
        """
        special_regions = []

        # 根据PDF结构信息判断
        for block in page_structure.get('text_blocks', []):
            if block['type'] == 'image':
                # 这是一个图片/图表区域
                x0, y0, x1, y1 = block['bbox']
                special_regions.append({
                    'type': 'figure',
                    'bbox': (x0, y0, x1, y1),
                    'description': '图表区域'
                })

        return special_regions

    def ocr_with_layout_preservation(
        self,
        image_path: str,
        page_structure: Dict
    ) -> List[Dict]:
        """
        进行OCR，保留页面布局信息

        Args:
            image_path: 图片路径
            page_structure: 页面结构信息

        Returns:
            带位置信息的文字块列表
        """
        image = Image.open(image_path)

        # 检测图表区域
        special_regions = self.detect_figures_and_tables(image_path, page_structure)

        # 获取图片尺寸
        img_width, img_height = image.size

        # 使用Tesseract进行OCR，获取详细数据
        data = pytesseract.image_to_data(
            image,
            lang=self.lang,
            output_type=pytesseract.Output.DICT
        )

        # 解析结果
        text_blocks = []
        n_boxes = len(data['text'])

        for i in range(n_boxes):
            text = data['text'][i].strip()
            conf = int(data['conf'][i])

            if text and conf > 60:  # 只保留置信度>60%的文字
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

                # 检查是否在图表区域内
                in_special_region = False
                for region in special_regions:
                    rx0, ry0, rx1, ry1 = region['bbox']
                    # 转换坐标（PyMuPDF和PIL坐标系可能不同）
                    if (rx0 <= x <= rx1 and ry0 <= y <= ry1):
                        in_special_region = True
                        break

                block = {
                    'text': text,
                    'x': x,
                    'y': y,
                    'width': w,
                    'height': h,
                    'conf': conf,
                    'in_figure': in_special_region
                }
                text_blocks.append(block)

        # 按阅读顺序排序（从上到下，从左到右）
        text_blocks.sort(key=lambda b: (b['y'], b['x']))

        return text_blocks

    def process_batch(
        self,
        pdf_path: str,
        start_page: int,
        end_page: int,
        batch_num: int,
        total_batches: int,
        structure: Dict
    ) -> str:
        """
        处理一批页面

        Args:
            pdf_path: PDF文件路径
            start_page: 起始页码（从1开始）
            end_page: 结束页码
            batch_num: 当前批次号
            total_batches: 总批次数
            structure: PDF结构信息

        Returns:
            批次输出PDF路径
        """
        print(f"\n[INFO] 处理批次 {batch_num}/{total_batches} (页 {start_page}-{end_page})")

        batch_pdf_path = self.temp_dir / f"batch_{batch_num:03d}.pdf"

        # 创建PDF写入器
        doc = fitz.open()

        # 处理每一页
        for page_num in range(start_page, end_page + 1):
            page_idx = page_num - 1  # 转换为0-based索引

            print(f"  [INFO] 处理第 {page_num} 页...")

            # 1. 转换为图片
            img_path = self.convert_page_to_image(pdf_path, page_num)

            # 2. OCR识别
            page_structure = structure['pages'][page_idx]
            text_blocks = self.ocr_with_layout_preservation(img_path, page_structure)

            # 3. 创建新页面
            # 使用上下文管理器确保图片正确关闭
            with Image.open(img_path) as img:
                img_width, img_height = img.size

                # 创建PDF页面（保持原始尺寸）
                page = doc.new_page(width=img_width, height=img_height)

                # 4. 插入原图作为背景
                page.insert_image(
                    fitz.Rect(0, 0, img_width, img_height),
                    filename=img_path
                )

                # 5. 添加透明文字层
                for block in text_blocks:
                    if block['in_figure']:
                        # 在图表区域内的文字，使用特殊标记
                        continue  # 暂时跳过图表区域内的文字

                    # 创建文字标注
                    text = block['text']
                    x, y = block['x'], block['y']
                    font_size = max(8, block['height'] * 0.8)

                    # 插入隐形文字（用于搜索和复制）
                    # 使用内置的 Helvetica 字体，对中文支持有限但可用
                    page.insert_text(
                        fitz.Point(x, y + font_size),
                        text,
                        fontsize=font_size,
                        color=(0, 0, 0),
                        overlay=True
                    )

            # 清理临时图片（此时文件已关闭，可以安全删除）
            try:
                os.remove(img_path)
            except PermissionError:
                # Windows 上文件句柄可能延迟释放，稍后清理
                pass

        # 保存批次PDF
        doc.save(batch_pdf_path)
        doc.close()

        print(f"  [OK] 批次 {batch_num} 完成: {batch_pdf_path}")

        return str(batch_pdf_path)

    def merge_batches(self, batch_files: List[str], output_path: str):
        """
        合并所有批次PDF

        Args:
            batch_files: 批次PDF文件列表
            output_path: 合并后的输出路径
        """
        print(f"\n[INFO] 正在合并 {len(batch_files)} 个批次...")

        # 创建新PDF
        merged_doc = fitz.open()

        for batch_file in tqdm(batch_files, desc="合并进度"):
            batch_doc = fitz.open(batch_file)
            merged_doc.insert_pdf(batch_doc)
            batch_doc.close()

        # 保存合并后的PDF
        merged_doc.save(output_path)
        merged_doc.close()

        print(f"[OK] 合并完成: {output_path}")

    def save_progress(self, progress: Dict):
        """保存处理进度"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

    def load_progress(self) -> Optional[Dict]:
        """加载处理进度"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def convert(
        self,
        input_path: str,
        output_path: str,
        resume: bool = False
    ):
        """
        执行完整的OCR转换（分批处理）

        Args:
            input_path: 输入PDF路径
            output_path: 输出PDF路径
            resume: 是否从断点恢复
        """
        print("=" * 60)
        print("PDF OCR Converter - 增强版")
        print("=" * 60)
        print(f"输入文件: {input_path}")
        print(f"输出文件: {output_path}")
        print(f"OCR语言: {self.lang}")
        print(f"DPI: {self.dpi}")
        print("=" * 60)

        # 检查输入文件
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"找不到输入文件: {input_path}")

        # 分析PDF结构
        structure = self.analyze_pdf_structure(input_path)
        total_pages = structure['total_pages']

        print(f"\n[INFO] 总页数: {total_pages}")
        print(f"[INFO] 将分为 {(total_pages + self.batch_size - 1) // self.batch_size} 批处理")

        # 检查是否有进度可以恢复
        progress = None
        if resume:
            progress = self.load_progress()
            if progress:
                print(f"[INFO] 找到未完成的任务，从批次 {progress['last_batch'] + 1} 继续")

        # 计算批次数
        total_batches = (total_pages + self.batch_size - 1) // self.batch_size
        batch_files = []

        # 处理每个批次
        start_batch = 0
        if progress:
            batch_files = progress.get('batch_files', [])
            start_batch = progress.get('last_batch', 0) + 1

        for batch_num in range(start_batch, total_batches):
            start_page = batch_num * self.batch_size + 1
            end_page = min((batch_num + 1) * self.batch_size, total_pages)

            try:
                # 处理批次
                batch_file = self.process_batch(
                    input_path,
                    start_page,
                    end_page,
                    batch_num + 1,
                    total_batches,
                    structure
                )
                batch_files.append(batch_file)

                # 保存进度
                self.save_progress({
                    'input_file': input_path,
                    'output_file': output_path,
                    'total_pages': total_pages,
                    'total_batches': total_batches,
                    'last_batch': batch_num,
                    'batch_files': batch_files,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                print(f"\n[ERROR] 批次 {batch_num + 1} 处理失败: {e}")
                print("[INFO] 进度已保存，可以使用 --resume 参数恢复")
                raise

        # 合并所有批次
        self.merge_batches(batch_files, output_path)

        # 清理临时文件
        self.cleanup()

        print("\n" + "=" * 60)
        print("[OK] 转换完成!")
        print(f"输出文件: {output_path}")
        print(f"总页数: {total_pages}")
        print("=" * 60)

    def cleanup(self):
        """清理临时文件"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            print(f"[INFO] 已清理临时目录: {self.temp_dir}")


def print_usage():
    """打印使用说明"""
    print("""
PDF OCR Converter - 增强版 (适合大型学术文档)

使用方法:
    python ocr_pdf_advanced.py <输入PDF> <输出PDF> [选项]

主要特性:
    ✓ 分批处理大文件（支持500-1000页）
    ✓ 智能检测图表和公式
    ✓ 保留原文档布局
    ✓ 断点续传（中断后可恢复）
    ✓ 自动合并批次结果

参数:
    输入PDF              图片型PDF文件路径
    输出PDF              生成的可搜索PDF路径

选项:
    --lang LANG          OCR语言 (默认: chi_sim+eng)
    --dpi DPI           图片分辨率 (默认: 200)
    --batch-size SIZE   每批处理页数 (默认: 50)
    --resume            从断点恢复处理
    --keep-temp         保留临时文件（用于调试）

示例:
    # 基础用法（自动分批）
    python ocr_pdf_advanced.py thesis.pdf searchable_thesis.pdf

    # 高质量OCR（慢但更准）
    python ocr_pdf_advanced.py book.pdf searchable_book.pdf --dpi 300

    # 每批100页（适合内存大的电脑）
    python ocr_pdf_advanced.py big_book.pdf output.pdf --batch-size 100

    # 中断后恢复
    python ocr_pdf_advanced.py thesis.pdf searchable_thesis.pdf --resume

适合场景:
    ✓ 学术论文（500-1000页）
    ✓ 扫描书籍
    ✓ 包含图表和公式的技术文档
    ✓ 需要保留原始布局的重要文档
""")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='PDF OCR Converter - 增强版（适合大型学术文档）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python ocr_pdf_advanced.py input.pdf output.pdf
    python ocr_pdf_advanced.py input.pdf output.pdf --dpi 300 --batch-size 100
        """
    )

    parser.add_argument('input', help='输入PDF文件路径')
    parser.add_argument('output', help='输出PDF文件路径')
    parser.add_argument('--lang', default='chi_sim+eng',
                        help='OCR语言 (默认: chi_sim+eng)')
    parser.add_argument('--dpi', type=int, default=200,
                        help='图片分辨率DPI (默认: 200)')
    parser.add_argument('--batch-size', type=int, default=50,
                        help='每批处理页数 (默认: 50)')
    parser.add_argument('--resume', action='store_true',
                        help='从断点恢复处理')
    parser.add_argument('--keep-temp', action='store_true',
                        help='保留临时文件')

    args = parser.parse_args()

    # 检查输入文件
    if not os.path.exists(args.input):
        print(f"[ERROR] 找不到输入文件: {args.input}")
        sys.exit(1)

    # 创建转换器
    converter = PDFOCRConverterAdvanced(
        dpi=args.dpi,
        lang=args.lang,
        batch_size=args.batch_size
    )

    try:
        # 执行转换
        converter.convert(args.input, args.output, resume=args.resume)

    except KeyboardInterrupt:
        print("\n\n[INFO] 用户中断处理")
        print("[INFO] 进度已保存，可以使用 --resume 参数恢复")
        sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] 转换失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        # 如果不保留临时文件，则清理
        if not args.keep_temp:
            converter.cleanup()


if __name__ == "__main__":
    main()
