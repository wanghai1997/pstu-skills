---
name: wechat-article-downloader
description: Download WeChat public account articles and convert them to PDF format. Use when Claude needs to download articles from WeChat official accounts, save them as PDF files for offline reading, annotation, or further processing with other skills like pdf manipulation. This skill fetches article content from WeChat URLs and generates clean, formatted PDF documents.
---

# WeChat Article Downloader

This skill downloads articles from WeChat public accounts and converts them to PDF format for offline access and further processing.

## Overview

WeChat official accounts contain valuable articles, but accessing them offline or archiving them can be challenging. This skill provides:

1. **Article Download** - Fetch article content from WeChat URLs
2. **PDF Conversion** - Convert articles to clean, readable PDF format
3. **Batch Processing** - Download multiple articles at once
4. **PDF Integration** - Seamlessly work with pdf skill for further processing

**Note:** By default, all downloaded articles include images. If you want to download articles without images, use the `--no-images` flag or explicitly tell Claude when requesting a download.

## Quick Start

### Download a Single Article

```python
from scripts.download_article import download_wechat_article

# Download single article to PDF
url = "https://mp.weixin.qq.com/s/ARTICLE_ID"
output_pdf = download_wechat_article(url, output_dir="./downloads")
print(f"Article saved as: {output_pdf}")
```

### Batch Download Articles

```python
from scripts.batch_download import batch_download

# Download multiple articles
articles = [
    {"url": "https://mp.weixin.qq.com/s/ID1", "title": "Article 1"},
    {"url": "https://mp.weixin.qq.com/s/ID2", "title": "Article 2"}
]

results = batch_download(articles, output_dir="./downloads")
print(f"Downloaded {len(results)} articles")
```

### Convert to PDF and Process

```bash
# Download article
python scripts/download_article.py "https://mp.weixin.qq.com/s/ARTICLE_ID"

# Now use pdf skill to merge with other PDFs
python skills/pdf/scripts/merge_pdfs.py downloads/*.pdf merged_output.pdf
```

## Scripts

### download_article.py

Downloads a single WeChat article and converts it to PDF.

**Usage:**
```bash
python scripts/download_article.py <article_url> [options]

Options:
  --output-dir PATH    Output directory (default: ./downloads)
  --filename NAME      Custom filename (default: auto-generated)
  --no-images          Exclude images (default: images are included)
  --timeout SECONDS    Request timeout (default: 30)
```

**Examples:**
```bash
# Basic download (includes images by default)
python scripts/download_article.py "https://mp.weixin.qq.com/s/xxxxx"

# Custom output directory and filename
python scripts/download_article.py "https://mp.weixin.qq.com/s/xxxxx" \
  --output-dir ./my_articles --filename "article_2024"

# Disable images for faster download
python scripts/download_article.py "https://mp.weixin.qq.com/s/xxxxx" \
  --no-images
```

### batch_download.py

Downloads multiple articles from a list.

**Usage:**
```bash
python scripts/batch_download.py <input_file> [options]

Input file format (JSON or CSV):
- JSON: [{"url": "...", "title": "..."}, ...]
- CSV: url,title
```

**Example:**
```bash
python scripts/batch_download.py articles_list.json --output-dir ./batch_output
```

### extract_links.py

Extracts article links from a WeChat account page or HTML file.

**Usage:**
```bash
python scripts/extract_links.py <source> [options]

Sources:
  - WeChat account URL: "https://mp.weixin.qq.com/mp/profile?src=..."
  - HTML file path: "./wechat_page.html"
  - Text file with URLs: "./urls.txt"
```

## Integration with PDF Skill

This skill works seamlessly with the pdf skill to enable powerful workflows:

### Example Workflow 1: Download and Merge

```bash
# Step 1: Download multiple articles
python scripts/batch_download.py articles_list.json --output-dir ./downloads

# Step 2: Merge all PDFs into one
python skills/pdf/scripts/merge_pdfs.py downloads/*.pdf combined_articles.pdf

# Step 3: Extract text for analysis
python -c "
from pypdf import PdfReader
reader = PdfReader('combined_articles.pdf')
text = '\n'.join([page.extract_text() for page in reader.pages])
print(f'Total characters: {len(text)}')
"
```

### Example Workflow 2: Download and Annotate

```bash
# Step 1: Download article
python scripts/download_article.py "https://mp.weixin.qq.com/s/xxxxx" \
  --output-dir ./temp

# Step 2: Add annotations using pdf skill
python skills/pdf/scripts/add_annotations.py temp/article.pdf annotations.json

# Step 3: Extract highlights
python skills/pdf/scripts/extract_highlights.py temp/article_annotated.pdf
```

### Example Workflow 3: Research Compilation

```bash
# Step 1: Extract all article links from a WeChat account
python scripts/extract_links.py "https://mp.weixin.qq.com/mp/profile?src=..." \
  > article_links.json

# Step 2: Download all articles
python scripts/batch_download.py article_links.json --output-dir ./research

# Step 3: Create table of contents
python -c "
import os
with open('research/toc.md', 'w', encoding='utf-8') as f:
    f.write('# Research Articles\\n\\n')
    for pdf in sorted(os.listdir('research')):
        if pdf.endswith('.pdf'):
            f.write(f'- [{pdf}]({pdf})\\n')
"
```

## Configuration

### Environment Variables

Create a `.env` file in the skill directory:

```bash
# Request settings
WECHAT_TIMEOUT=30
MAX_RETRIES=3
RATE_LIMIT_DELAY=1.0

# PDF generation
PDF_PAGE_SIZE=A4
PDF_MARGIN=20mm
INCLUDE_METADATA=true

# Output settings
DEFAULT_OUTPUT_DIR=./downloads
ORGANIZE_BY_DATE=true  # Create subdirectories by date
```

### Authentication (if needed)

For accounts requiring login:

```bash
# In .env file
WECHAT_COOKIE="your_cookie_string"
USER_AGENT="your_user_agent_string"
```

## Input Formats

### Direct URL
Single article URL: `https://mp.weixin.qq.com/s/xxxxx`

### Batch List (JSON)
```json
[
  {
    "url": "https://mp.weixin.qq.com/s/article1",
    "title": "Article Title 1",
    "tags": ["tag1", "tag2"]
  },
  {
    "url": "https://mp.weixin.qq.com/s/article2",
    "title": "Article Title 2"
  }
]
```

### Batch List (CSV)
```csv
url,title,tags
https://mp.weixin.qq.com/s/article1,Title 1,"tag1,tag2"
https://mp.weixin.qq.com/s/article2,Title 2,
```

## Output Format

### PDF Structure

Generated PDFs include:
- **Title page**: Article title, source, date
- **Content**: Formatted article body with proper headings
- **Images**: Embedded images (if enabled)
- **Metadata**: PDF metadata with article information
- **Links**: Clickable links preserved

### File Organization

```
downloads/
├── 2024-01-15/
│   ├── article-title-1.pdf
│   ├── article-title-2.pdf
│   └── metadata.json
├── 2024-01-16/
│   └── article-title-3.pdf
└── archive/
    └── combined-monthly.pdf
```

## Troubleshooting

**Issue:** Article download fails with timeout
- **Solution:** Increase timeout in `.env`: `WECHAT_TIMEOUT=60`

**Issue:** PDF generation fails for certain articles
- **Solution:** Some articles use complex JavaScript. Try disabling images: `--include-images false`

**Issue:** Batch download stops midway
- **Solution:** Check network connection. Resume by removing already-downloaded URLs from list.

**Issue:** Chinese characters display incorrectly in PDF
- **Solution:** Ensure proper font is installed. Set `PDF_FONT=simhei.ttf` in `.env`

**Issue:** Links not clickable in PDF
- **Solution:** Update to latest version. Some older versions don't preserve links.

## Best Practices

1. **Rate Limiting**: Add delays between requests (default 1 second)
2. **Batch Processing**: Download in small batches (10-20 articles) to avoid failures
3. **File Naming**: Use descriptive names for easy identification
4. **Organization**: Use date-based subdirectories for large collections
5. **Backup**: Keep original JSON/CSV lists for re-downloading if needed
6. **Validation**: Always verify a few PDFs before downloading large batches

## Examples

### Example 1: Download Research Articles

```python
from scripts.batch_download import batch_download

research_articles = [
    {"url": "https://mp.weixin.qq.com/s/ai-research-2024", "title": "AI Advances 2024"},
    {"url": "https://mp.weixin.qq.com/s/ml-breakthrough", "title": "ML Breakthrough"},
    {"url": "https://mp.weixin.qq.com/s/data-science-trends", "title": "Data Science Trends"}
]

results = batch_download(research_articles, output_dir="./research_papers")
print(f"Successfully downloaded {len(results)} research papers")
```

### Example 2: Create Study Collection

```bash
# 1. Extract all articles from a WeChat account
python scripts/extract_links.py "https://mp.weixin.qq.com/mp/profile?src=..." \
  | grep -E "(AI|machine learning|data)" > ai_articles.json

# 2. Download only AI-related articles
python scripts/batch_download.py ai_articles.json --output-dir ./ai_study

# 3. Merge into study guide
python skills/pdf/scripts/merge_pdfs.py ai_study/*.pdf AI_Study_Guide.pdf
```

### Example 3: Automated Archive

```bash
#!/bin/bash
# daily-archive.sh - Archive today's articles

DATE=$(date +%Y-%m-%d)
OUTPUT_DIR="./archive/$DATE"

# Download new articles
python scripts/batch_download.py subscription_list.json \
  --output-dir "$OUTPUT_DIR"

# Create index with titles
python scripts/create_index.py "$OUTPUT_DIR" > "$OUTPUT_DIR/index.md"

# Generate summary PDF
python skills/pdf/scripts/convert_markdown_to_pdf.py \
  "$OUTPUT_DIR/index.md" "$OUTPUT_DIR/INDEX.pdf"

echo "Archived $(ls $OUTPUT_DIR/*.pdf | wc -l) articles to $OUTPUT_DIR"
```

## Dependencies

- Python 3.8+
- requests - HTTP library
- beautifulsoup4 - HTML parsing
- weasyprint or pdfkit - PDF generation
- pydantic - Data validation
- tqdm - Progress bars

Install dependencies:
```bash
pip install requests beautifulsoup4 weasyprint pydantic tqdm
```

## License

See LICENSE.txt for complete terms.
