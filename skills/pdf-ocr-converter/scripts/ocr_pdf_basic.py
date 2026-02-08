#!/usr/bin/env python3
"""
PDF OCR Converter
将图片型PDF转换为文本型PDF（可搜索、可复制）

使用方法:
    python ocr_pdf.py input.pdf output.pdf [选项]

示例:
    python ocr_pdf.py scanned.pdf searchable.pdf
    python ocr_pdf.py scanned.pdf searchable.pdf --lang chi_sim+eng --dpi 300
"""

import sys
import os
import argparse
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional

# PDF处理
from pdf2image import convert_from_path
from PIL import Image

# OCR
import pytesseract

# PDF生成
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PDFOCRConverter:
    """PDF OCR转换器"""

    def __init__(self, dpi: int = 200, lang: str = 'chi_sim+eng'):
        """
        初始化转换器

        Args:
            dpi: 转换图片的分辨率（默认200，越高越清晰但越慢）
            lang: OCR语言（默认中文简体+英文）
        """
        self.dpi = dpi
        self.lang = lang
        self.temp_dir = None

        # 注册中文字体（如果可用）
        self._register_fonts()

    def _register_fonts(self):
        """注册中文字体"""
        try:
            # 尝试注册常见的开源中文字体
            font_paths = [
                'C:/Windows/Fonts/simhei.ttf',  # Windows 黑体
                'C:/Windows/Fonts/simsun.ttc',  # Windows 宋体
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',  # Linux 文泉驿
                '/System/Library/Fonts/PingFang.ttc',  # Mac 苹方
            ]

            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        self.chinese_font = 'ChineseFont'
                        print(f"[OK] 已加载字体: {font_path}")
                        return
                    except:
                        continue

            # 如果没有找到中文字体，使用默认字体
            self.chinese_font = 'Helvetica'
            print("[WARNING] 未找到中文字体，使用默认字体（中文可能显示为方框）")

        except Exception as e:
            self.chinese_font = 'Helvetica'
            print(f"[WARNING] 字体加载失败: {e}")

    def pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """
        将PDF转换为图片列表

        Args:
            pdf_path: PDF文件路径

        Returns:
            图片列表（每页一个图片）
        """
        print(f"[INFO] 正在将PDF转换为图片 (DPI={self.dpi})...")

        try:
            images = convert_from_path(
                pdf_path,
                dpi=self.dpi,
                fmt='png',
                transparent=False
            )

            print(f"[OK] 成功转换 {len(images)} 页")
            return images

        except Exception as e:
            print(f"[ERROR] PDF转图片失败: {e}")
            print("[HINT] 请确保已安装 poppler:")
            print("  Windows: 下载 https://github.com/oschwartz10612/poppler-windows/releases/")
            print("  Mac: brew install poppler")
            print("  Linux: sudo apt-get install poppler-utils")
            raise

    def ocr_image(self, image: Image.Image) -> List[dict]:
        """
        对图片进行OCR识别

        Args:
            image: PIL图片对象

        Returns:
            识别的文字块列表，每个包含text和位置信息
        """
        try:
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

                # 只保留置信度>60%的文字
                if text and conf > 60:
                    block = {
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'conf': conf
                    }
                    text_blocks.append(block)

            return text_blocks

        except Exception as e:
            print(f"[ERROR] OCR识别失败: {e}")
            print("[HINT] 请确保已安装Tesseract并配置正确")
            raise

    def create_searchable_pdf(
        self,
        images: List[Image.Image],
        output_path: str,
        text_blocks_list: List[List[dict]]
    ):
        """
        创建可搜索的PDF

        Args:
            images: 原始图片列表
            output_path: 输出PDF路径
            text_blocks_list: 每页的文字块列表
        """
        print(f"[INFO] 正在生成可搜索PDF...")

        # 创建PDF
        c = canvas.Canvas(output_path, pagesize=A4)

        for page_num, (image, text_blocks) in enumerate(zip(images, text_blocks_list)):
            print(f"[INFO] 处理第 {page_num + 1}/{len(images)} 页...")

            # 获取图片尺寸
            img_width, img_height = image.size

            # 计算缩放比例以适应A4页面
            a4_width, a4_height = A4
            scale_x = a4_width / img_width
            scale_y = a4_height / img_height
            scale = min(scale_x, scale_y)

            # 计算居中位置
            new_width = img_width * scale
            new_height = img_height * scale
            x_offset = (a4_width - new_width) / 2
            y_offset = (a4_height - new_height) / 2

            # 临时保存图片
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
                image.save(tmp_path, 'PNG')

            # 绘制图片（背景）
            c.drawImage(tmp_path, x_offset, y_offset, width=new_width, height=new_height)

            # 绘制文字层（透明，可搜索）
            c.setFillColorRGB(0, 0, 0, alpha=0)  # 完全透明
            c.setFont(self.chinese_font, 12)

            for block in text_blocks:
                # 计算缩放后的位置
                x = x_offset + block['x'] * scale
                y = y_offset + new_height - (block['y'] + block['height']) * scale

                # 绘制透明文字（用于搜索和复制）
                text = block['text']
                font_size = max(8, block['height'] * scale * 0.8)

                try:
                    c.setFont(self.chinese_font, font_size)
                    c.drawString(x, y, text)
                except:
                    # 如果中文字体失败，使用默认字体
                    c.setFont('Helvetica', font_size)
                    c.drawString(x, y, text)

            # 删除临时图片
            os.unlink(tmp_path)

            # 新建一页
            c.showPage()

        # 保存PDF
        c.save()
        print(f"[OK] PDF已保存: {output_path}")

    def convert(
        self,
        input_path: str,
        output_path: str,
        pages: Optional[str] = None,
        keep_images: bool = False
    ):
        """
        执行完整的OCR转换

        Args:
            input_path: 输入PDF路径
            output_path: 输出PDF路径
            pages: 指定页面范围（如 "1-5" 或 "1,3,5"）
            keep_images: 是否保留临时图片
        """
        # 检查输入文件
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"找不到输入文件: {input_path}")

        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        print(f"[INFO] 临时目录: {self.temp_dir}")

        try:
            # 1. PDF转图片
            images = self.pdf_to_images(input_path)

            # 如果指定了页面范围
            if pages:
                page_indices = self._parse_page_range(pages, len(images))
                images = [images[i] for i in page_indices]
                print(f"[INFO] 仅处理指定页面: {pages}")

            # 2. 对每页进行OCR
            all_text_blocks = []
            for i, image in enumerate(images):
                print(f"[INFO] 正在OCR识别第 {i + 1}/{len(images)} 页...")
                text_blocks = self.ocr_image(image)
                all_text_blocks.append(text_blocks)
                print(f"[OK] 识别到 {len(text_blocks)} 个文字块")

            # 3. 创建可搜索PDF
            self.create_searchable_pdf(images, output_path, all_text_blocks)

            # 4. 验证输出
            self._verify_output(output_path)

            print(f"\n[OK] 转换完成!")
            print(f"  输入: {input_path}")
            print(f"  输出: {output_path}")
            print(f"  页数: {len(images)}")

        finally:
            # 清理临时文件
            if not keep_images and self.temp_dir:
                import shutil
                shutil.rmtree(self.temp_dir, ignore_errors=True)
                print(f"[INFO] 已清理临时文件")

    def _parse_page_range(self, pages: str, total_pages: int) -> List[int]:
        """解析页面范围字符串"""
        indices = []

        for part in pages.split(','):
            part = part.strip()
            if '-' in part:
                start, end = part.split('-')
                start = int(start) - 1 if start else 0
                end = int(end) if end else total_pages
                indices.extend(range(start, min(end, total_pages)))
            else:
                indices.append(int(part) - 1)

        return sorted(set(indices))

    def _verify_output(self, output_path: str):
        """验证输出PDF"""
        try:
            from pypdf import PdfReader
            reader = PdfReader(output_path)

            # 尝试提取文字
            sample_text = ""
            for i, page in enumerate(reader.pages[:3]):  # 检查前3页
                text = page.extract_text()
                if text:
                    sample_text += text[:100]  # 取前100字符

            if sample_text.strip():
                print(f"[OK] 验证成功: PDF包含可提取文字")
                print(f"[INFO] 文字示例: {sample_text[:80]}...")
            else:
                print(f"[WARNING] 验证警告: PDF中未检测到文字")

        except Exception as e:
            print(f"[WARNING] 验证失败: {e}")


def print_usage():
    """打印使用说明"""
    print("""
PDF OCR Converter - 将图片型PDF转换为文本型PDF

使用方法:
    python ocr_pdf.py <输入PDF> <输出PDF> [选项]

参数:
    输入PDF              图片型PDF文件路径
    输出PDF              生成的可搜索PDF路径

选项:
    --lang LANG          OCR语言 (默认: chi_sim+eng)
                         可选: chi_sim(中文简体), chi_tra(中文繁体)
                               eng(英文), jpn(日文), kor(韩文)
                         多个语言用+连接，如: chi_sim+eng

    --dpi DPI           图片分辨率 (默认: 200)
                        越高越清晰但越慢，推荐: 150-300

    --pages PAGES       指定页面范围 (默认: 全部)
                        示例: --pages 1-5  或 --pages 1,3,5

    --keep-images       保留临时图片（用于调试）

示例:
    # 基本用法
    python ocr_pdf.py scanned.pdf searchable.pdf

    # 指定中文OCR
    python ocr_pdf.py scanned.pdf searchable.pdf --lang chi_sim

    # 高质量OCR（较慢）
    python ocr_pdf.py scanned.pdf searchable.pdf --dpi 300

    # 只处理前10页
    python ocr_pdf.py scanned.pdf searchable.pdf --pages 1-10

依赖安装:
    pip install -r ../requirements.txt

注意:
    使用前请确保已安装Tesseract OCR:
    - Windows: https://github.com/UB-Mannheim/tesseract/wiki
    - Mac: brew install tesseract
    - Linux: sudo apt-get install tesseract-ocr
""")


def main():
    """主函数"""
    # 检查命令行参数
    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    # 解析参数
    parser = argparse.ArgumentParser(
        description='将图片型PDF转换为文本型PDF（可搜索、可复制）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python ocr_pdf.py scanned.pdf output.pdf
    python ocr_pdf.py scanned.pdf output.pdf --lang chi_sim --dpi 300
        """
    )

    parser.add_argument('input', help='输入PDF文件路径')
    parser.add_argument('output', help='输出PDF文件路径')
    parser.add_argument('--lang', default='chi_sim+eng',
                        help='OCR语言 (默认: chi_sim+eng)')
    parser.add_argument('--dpi', type=int, default=200,
                        help='图片分辨率DPI (默认: 200)')
    parser.add_argument('--pages', default=None,
                        help='指定页面范围，如: 1-5 或 1,3,5')
    parser.add_argument('--keep-images', action='store_true',
                        help='保留临时图片文件')

    args = parser.parse_args()

    # 检查输入文件
    if not os.path.exists(args.input):
        print(f"[ERROR] 找不到输入文件: {args.input}")
        sys.exit(1)

    # 检查输出目录
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 创建转换器并执行
    try:
        converter = PDFOCRConverter(dpi=args.dpi, lang=args.lang)
        converter.convert(
            args.input,
            args.output,
            pages=args.pages,
            keep_images=args.keep_images
        )
    except Exception as e:
        print(f"\n[ERROR] 转换失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
