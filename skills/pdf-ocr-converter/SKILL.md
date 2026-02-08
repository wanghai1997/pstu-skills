---
name: pdf-ocr-converter
description: Convert image-based PDFs (scanned documents) to text-based PDFs with searchable and copyable text. Use when Claude needs to process scanned PDFs, image-only PDFs, or documents where text cannot be selected. This skill performs OCR (Optical Character Recognition) to extract text from images and creates a new PDF with embedded text layer, making it readable by AI models and searchable by humans.
---

# PDF OCR Converter

This skill transforms image-based PDFs (where each page is just a picture) into text-based PDFs (where text is selectable, copyable, and searchable).

## Why This Matters

**Problem**: Many PDFs are actually just images:
- Scanned books and papers
- Old documents converted to PDF
- Photos of documents saved as PDF
- Screenshots compiled into PDF

These "image PDFs" cannot be:
- ❌ Read by AI models (Claude, GPT, etc.)
- ❌ Searched for keywords
- ❌ Copied and pasted
- ❌ Processed by text analysis tools

**Solution**: This skill uses OCR (Optical Character Recognition) to:
1. Convert each PDF page to an image
2. Recognize text in the image using AI
3. Create a new PDF with the recognized text embedded
4. Preserve the original visual appearance

## How It Works (Simple Analogy)

Imagine you have a printed book and you want to make it searchable:

**Traditional way**: Manually type every word ❌

**This skill**: Like a super-fast reader who:
1. Takes a photo of each page (PDF → Image)
2. Reads and memorizes all text (OCR)
3. Types it into a computer (Create text PDF)
4. Keeps the original formatting (Preserve layout)

## Quick Start

### 选择适合的版本

我们提供两个版本：

**基础版** (`ocr_pdf_basic.py`)：适合小文件（<100页）
```bash
python scripts/ocr_pdf_basic.py input_scanned.pdf output_text.pdf
```

**增强版** (`ocr_pdf_advanced.py`)：适合大型学术文档（500-1000页）
```bash
python scripts/ocr_pdf_advanced.py input_scanned.pdf output_text.pdf
```

### 转换大型学术文档（500-1000页）

```bash
# 自动分批处理（每批50页，适合大多数电脑）
python scripts/ocr_pdf_advanced.py large_thesis.pdf output.pdf

# 如果内存充足，可以增加每批页数
python scripts/ocr_pdf_advanced.py large_thesis.pdf output.pdf --batch-size 100

# 高质量OCR（适合包含图表和公式的论文）
python scripts/ocr_pdf_advanced.py large_thesis.pdf output.pdf --dpi 300

# 如果中断，可以恢复
python scripts/ocr_pdf_advanced.py large_thesis.pdf output.pdf --resume
```

### Advanced Options

```bash
# Specify language (default: Chinese + English)
python scripts/ocr_pdf.py input.pdf output.pdf --lang chi_sim+eng

# Higher quality OCR (slower but more accurate)
python scripts/ocr_pdf.py input.pdf output.pdf --dpi 300

# Process only specific pages
python scripts/ocr_pdf.py input.pdf output.pdf --pages 1-10

# Keep temporary images for debugging
python scripts/ocr_pdf.py input.pdf output.pdf --keep-images
```

## Installation

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Tesseract OCR Engine

**Windows**:
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and remember the path (e.g., `C:\Program Files\Tesseract-OCR`)
3. Add to system PATH or set environment variable:
   ```bash
   setx TESSDATA_PREFIX "C:\Program Files\Tesseract-OCR\tessdata"
   ```

**Mac**:
```bash
brew install tesseract tesseract-lang
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng
```

### Step 3: Download Language Data (if needed)

For Chinese OCR:
- Windows: Already included in installer
- Mac/Linux: `tesseract-lang` package includes Chinese

## Usage Examples

### Example 1: Process a Scanned Paper

```bash
# You have a scanned research paper
python scripts/ocr_pdf.py scanned_paper.pdf searchable_paper.pdf

# Now you can:
# - Search for keywords
# - Copy text to clipboard
# - Let Claude read and summarize it
```

### Example 2: Batch Process Multiple PDFs

```bash
# Create a script to process all PDFs in a folder
for pdf in *.pdf; do
    python scripts/ocr_pdf.py "$pdf" "ocr_${pdf}"
done
```

### Example 3: Integrate with PDF Skill

```bash
# Step 1: OCR the scanned PDF
python skills/pdf-ocr-converter/scripts/ocr_pdf.py scanned.pdf searchable.pdf

# Step 2: Now use pdf skill to extract text
python skills/pdf/scripts/extract_text.py searchable.pdf

# Step 3: Or merge with other PDFs
python skills/pdf/scripts/merge_pdfs.py searchable.pdf other.pdf combined.pdf
```

## Technical Details

### OCR Process Flow

**基础版（小文件）：**
```
Input: Image-based PDF
    ↓
[1] Convert PDF pages to images (pdf2image)
    ↓
[2] Perform OCR on each image (Tesseract)
    ↓
[3] Extract text with position information
    ↓
[4] Create new PDF with text layer (reportlab)
    ↓
[5] Overlay text on original images (optional)
    ↓
Output: Text-based PDF (searchable + copyable)
```

**增强版（大文件，500-1000页）：**
```
Input: Large Image-based PDF (500-1000 pages)
    ↓
[1] Analyze PDF structure (PyMuPDF)
    ↓
[2] Detect figures, tables, formulas
    ↓
[3] Split into batches (e.g., 50 pages/batch)
    ↓
[4] Process each batch:
    ├─ Convert to images
    ├─ OCR with layout preservation
    ├─ Detect and preserve figures
    └─ Save batch PDF
    ↓
[5] Merge all batches
    ↓
[6] Optimize final PDF
    ↓
Output: Complete searchable PDF (with figures preserved)
```

### Handling Large Documents (500-1000 pages)

**Why Batch Processing?**

Processing a 1000-page PDF at once would:
- ❌ Consume 8-16GB RAM (may crash)
- ❌ Take 2-4 hours without progress feedback
- ❌ Lose all progress if interrupted
- ❌ Generate huge temporary files

**Our Solution: Smart Batch Processing**

```python
# Automatic batch splitting
Batch 1: Pages 1-50
Batch 2: Pages 51-100
...
Batch N: Pages 951-1000

# Benefits:
✓ Memory efficient (only 50 pages in RAM at a time)
✓ Progress feedback ("Processing batch 5/20")
✓ Resume capability (save progress after each batch)
✓ Parallel processing ready (future enhancement)
```

**Resume Capability**

If conversion is interrupted:
```bash
# Normal start
python ocr_pdf_advanced.py thesis.pdf output.pdf
# ... processing batch 8/20 ...
# [CTRL+C] User interrupts

# Resume from batch 8
python ocr_pdf_advanced.py thesis.pdf output.pdf --resume
# [INFO] Resuming from batch 8/20...
```

### Preserving Figures and Formulas

**The Challenge**

Academic papers contain:
- 📊 Charts and graphs
- 📈 Data visualizations
- 🧮 Mathematical formulas
- 🔬 Technical diagrams

Simple OCR would:
- ❌ Convert everything to text (destroying visuals)
- ❌ Lose formula formatting
- ❌ Remove color from charts

**Our Approach: Layered PDF**

```
PDF Structure:
┌─────────────────────────────────┐
│  Layer 1: Original Image        │  ← Preserved exactly
│  [Chart/Formula/Diagram]        │     (visual fidelity)
├─────────────────────────────────┤
│  Layer 2: OCR Text (invisible)  │  ← For search/copy
│  [Recognized text content]      │     (transparent)
└─────────────────────────────────┘

Result: Looks identical, but searchable!
```

**Formula Handling**

For mathematical formulas:
1. **Detection**: Identify formula regions (heuristic: special chars like ∑, ∫, α)
2. **Preservation**: Keep original image (formulas are hard to OCR accurately)
3. **Alternative**: Use LaTeX-OCR for formula-specific recognition (future)

**Figure Handling**

For charts and diagrams:
1. **Detection**: Large image regions with minimal text
2. **Preservation**: Keep original high-resolution image
3. **Caption OCR**: Extract figure captions for searchability

### Supported Languages

- **Chinese (Simplified)**: `chi_sim`
- **Chinese (Traditional)**: `chi_tra`
- **English**: `eng`
- **Japanese**: `jpn`
- **Korean**: `kor`
- **And 100+ more...**

Specify multiple languages: `--lang chi_sim+eng`

### Quality vs Speed Trade-off

| DPI | Quality | Speed | Use Case |
|-----|---------|-------|----------|
| 150 | Good | Fast | Draft documents, quick preview |
| 200 | Better | Medium | Most documents (recommended) |
| 300 | Best | Slow | Important documents, small text |
| 400+ | Excellent | Very Slow | Rarely needed |

**Default**: 200 DPI (good balance)

## Troubleshooting

### Issue: "Tesseract not found"

**Solution**: Install Tesseract and add to PATH

Windows:
```bash
# Check if installed
tesseract --version

# If not found, add to PATH manually
set PATH=%PATH%;C:\Program Files\Tesseract-OCR
```

### Issue: Chinese characters not recognized

**Solution**: Install Chinese language data

Windows:
- Re-run installer and select Chinese languages

Mac/Linux:
```bash
# Mac
brew install tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr-chi-sim
```

### Issue: Poor OCR accuracy

**Try these solutions**:

1. **Increase DPI**:
   ```bash
   python scripts/ocr_pdf.py input.pdf output.pdf --dpi 300
   ```

2. **Check image quality**:
   - Original scan should be clear
   - No heavy compression artifacts
   - Good contrast (black text on white background)

3. **Specify correct language**:
   ```bash
   python scripts/ocr_pdf.py input.pdf output.pdf --lang chi_sim
   ```

4. **Pre-process the PDF**:
   - Use higher quality scans
   - Ensure pages are straight (not rotated)
   - Remove shadows and noise if possible

### Issue: Very slow processing

**Solutions**:

1. **Lower DPI** (if quality allows):
   ```bash
   python scripts/ocr_pdf.py input.pdf output.pdf --dpi 150
   ```

2. **Process fewer pages**:
   ```bash
   python scripts/ocr_pdf.py input.pdf output.pdf --pages 1-5
   ```

3. **Use faster OCR mode**:
   - Edit script to use `--psm 6` (single uniform block of text)
   - Instead of `--psm 3` (fully automatic page segmentation)

## Best Practices

### 1. Pre-process for Better Results

Before OCR:
- ✅ Ensure scans are straight (not tilted)
- ✅ Use high enough resolution (150+ DPI)
- ✅ Ensure good contrast
- ❌ Don't use heavily compressed images
- ❌ Don't use blurry or low-quality scans

### 2. Verify Output

Always check a few pages of the output:
- Open the PDF and try searching for text
- Copy some text and paste it to verify accuracy
- Check if formatting is preserved

### 3. Handle Large Documents

For books or long documents:
```bash
# Process in chunks
python scripts/ocr_pdf.py book.pdf part1.pdf --pages 1-50
python scripts/ocr_pdf.py book.pdf part2.pdf --pages 51-100
# ... then merge
python skills/pdf/scripts/merge_pdfs.py part*.pdf full_book.pdf
```

### 4. Keep Originals

Always keep the original scanned PDF:
- OCR is not 100% perfect
- You might need to re-process with different settings
- Original has exact visual fidelity

## Integration with AI Workflows

### Workflow 1: AI Document Analysis

```bash
# 1. OCR the scanned document
python scripts/ocr_pdf.py scanned_contract.pdf searchable_contract.pdf

# 2. Extract text for AI analysis
text=$(python -c "from pypdf import PdfReader; print(PdfReader('searchable_contract.pdf').pages[0].extract_text())")

# 3. Send to AI for analysis
# "Please summarize this contract: $text"
```

### Workflow 2: Searchable Archive

```bash
# OCR all scanned documents
for pdf in scanned_documents/*.pdf; do
    python scripts/ocr_pdf.py "$pdf" "ocr_${pdf}"
done

# Now you can search across all documents
# using pdf skill or desktop search tools
```

### Workflow 3: Data Extraction

```bash
# OCR a form
python scripts/ocr_pdf.py scanned_form.pdf searchable_form.pdf

# Extract structured data using pdf skill
python skills/pdf/scripts/extract_form_field_info.py searchable_form.pdf
```

## Performance Tips

### Speed Optimization

1. **Use SSD**: OCR involves heavy disk I/O
2. **More RAM**: For processing large PDFs
3. **Multi-threading**: Process multiple pages in parallel (advanced)
4. **Lower DPI**: When quality requirements allow

### Quality Optimization

1. **Higher DPI**: For small text or complex layouts
2. **Correct language**: Specify exact language(s)
3. **Clean scans**: Remove noise and artifacts
4. **Deskew**: Ensure text is horizontal

## Limitations

### What Works Well
- ✅ Printed text (books, papers, forms)
- ✅ Clear, high-contrast documents
- ✅ Standard fonts
- ✅ Single column layouts

### What Doesn't Work Well
- ❌ Handwritten text (use specialized handwriting OCR)
- ❌ Very stylized or decorative fonts
- ❌ Extreme angles or warped pages
- ❌ Very low resolution (below 100 DPI)
- ❌ Complex multi-column magazine layouts

### Accuracy Expectations

- **Perfect scans**: 95-99% accuracy
- **Good scans**: 85-95% accuracy
- **Average scans**: 70-85% accuracy
- **Poor scans**: Below 70% accuracy

Always proofread important documents!

## Advanced Usage

### Custom OCR Configuration

Edit `scripts/ocr_pdf.py` to customize Tesseract settings:

```python
# Example: Use LSTM neural network (more accurate, slower)
custom_config = r'--oem 3 --psm 3 -c tessedit_char_whitelist=0123456789'
# Only recognize digits

# Example: Preserve interword spaces
custom_config = r'--preserve_interword_spaces 1'
```

### Integration with Other Tools

```python
# After OCR, use with other skills
from skills.pdf.scripts.extract_text import extract_text
from skills.pdf.scripts.merge_pdfs import merge_pdfs

# Your OCR + processing pipeline here
```

## References

- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- pytesseract docs: https://pypi.org/project/pytesseract/
- pdf2image docs: https://pypi.org/project/pdf2image/
- reportlab docs: https://www.reportlab.com/docs/reportlab-userguide.pdf

## License

See LICENSE.txt for complete terms.
