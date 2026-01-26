---
name: experiment-report-processor
description: Process and analyze experimental data for scientific research. Use when Claude needs to work with experiment data files, generate standardized reports, and organize results into structured formats. This skill handles common data formats (CSV, Excel, JSON) and creates publication-ready reports for scientific research.
---

# Experiment Report Processor

This skill helps process experimental data and generate standardized scientific reports for research purposes.

## Overview

When working with experimental data, this skill provides:
1. Data validation and cleaning
2. Statistical analysis and visualization
3. Report generation from templates
4. Result organization and formatting

## Quick Start

### Process Experiment Data

```python
from scripts.process_data import process_experiment_file

# Process a data file
results = process_experiment_file("experiment_data.csv")
print(f"Processed {results['sample_count']} samples")
print(f"Mean value: {results['mean']}")
print(f"Standard deviation: {results['std_dev']}")
```

### Generate Report

```python
from scripts.generate_report import create_experiment_report

# Generate report from processed data
create_experiment_report(
    data=results,
    template="assets/report_template.md",
    output="experiment_report.md"
)
```

## Scripts

### process_data.py

Processes experimental data files and returns structured results.

**Usage:**
```python
python scripts/process_data.py <input_file> [options]
```

**Supported formats:**
- CSV (.csv)
- Excel (.xlsx, .xls)
- JSON (.json)

**Outputs:**
- Cleaned dataset
- Statistical summary
- Data quality report

### generate_report.py

Generates formatted experiment reports from processed data.

**Usage:**
```python
python scripts/generate_report.py <processed_data> --template <template> --output <output_file>
```

## Templates

Use the templates in `assets/` directory to customize report formatting:

- `report_template.md` - Standard experimental report format
- `lab_report_template.md` - Laboratory-specific format
- `field_study_template.md` - Field study format

## Best Practices

1. **Data Validation:** Always validate data quality before processing
2. **Backup Originals:** Keep original data files unchanged
3. **Document Parameters:** Record all processing parameters for reproducibility
4. **Version Control:** Track changes to processing scripts

## Common Workflows

### Workflow 1: Basic Data Processing

1. Load experimental data file
2. Validate data quality and structure
3. Clean and standardize data format
4. Calculate summary statistics
5. Export processed data

### Workflow 2: Report Generation

1. Process data as in Workflow 1
2. Select appropriate template
3. Generate report with charts and analysis
4. Review and refine report content
5. Export to final format (PDF, Word, etc.)

## Troubleshooting

**Issue:** Data file cannot be loaded
- **Solution:** Check file format and encoding. Ensure file is not open in another program.

**Issue:** Statistical calculations fail
- **Solution:** Check for missing or invalid values in data. Verify data types are correct.

**Issue:** Report generation fails
- **Solution:** Verify template file exists and has correct format. Check that all required variables are provided.
