# PDF OCR Converter

将图片型PDF（扫描文档）转换为文本型PDF（可搜索、可复制）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 安装Tesseract OCR

**Windows**:
1. 下载: https://github.com/UB-Mannheim/tesseract/wiki
2. 安装时选择中文语言包
3. 将安装目录添加到系统PATH

**Mac**:
```bash
brew install tesseract tesseract-lang
```

**Linux**:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
```

### 3. 转换PDF

```bash
cd scripts
python ocr_pdf.py input_scanned.pdf output_searchable.pdf
```

## 功能特点

- ✅ 支持中文、英文及100+种语言
- ✅ 保留原始PDF视觉外观
- ✅ 生成可搜索、可复制的文字层
- ✅ 支持指定页面范围处理
- ✅ 可调节OCR质量（DPI设置）

## 使用示例

### 基础用法
```bash
python ocr_pdf.py scanned_document.pdf searchable_document.pdf
```

### 仅中文OCR
```bash
python ocr_pdf.py scanned.pdf searchable.pdf --lang chi_sim
```

### 高质量OCR（较慢但更精准）
```bash
python ocr_pdf.py scanned.pdf searchable.pdf --dpi 300
```

### 仅处理前10页
```bash
python ocr_pdf.py scanned.pdf searchable.pdf --pages 1-10
```

## 工作原理

1. **PDF → 图片**: 将PDF每页转换为高清图片
2. **OCR识别**: 使用Tesseract识别图片中的文字
3. **生成新PDF**: 创建包含文字层的新PDF
4. **叠加文字**: 在原始图片上叠加透明的可搜索文字

## 常见问题

### Q: OCR识别准确率如何？
A: 取决于扫描质量：
- 清晰扫描：95-99%准确率
- 一般扫描：85-95%准确率
- 模糊扫描：70-85%准确率

### Q: 支持手写文字吗？
A: 不支持。本工具专为印刷体设计。手写文字需要专门的模型。

### Q: 处理速度如何？
A: 取决于PDF页数和DPI：
- 10页PDF @ 200 DPI：约30-60秒
- 100页PDF @ 200 DPI：约5-10分钟

## 技术栈

- **pdf2image**: PDF转图片
- **Tesseract OCR**: 开源OCR引擎
- **pytesseract**: Python Tesseract接口
- **reportlab**: PDF生成

## 许可

MIT License
