# BehaveX Utility Scripts

This folder contains utility scripts for BehaveX that help with common tasks and maintenance.

## Available Scripts

### generate_html_from_json.py

Generate HTML reports from existing `report.json` files without re-running tests.

**Usage:**
```bash
python scripts/generate_html_from_json.py <path_to_report.json> [output_directory]
```

**Examples:**
```bash
# Generate HTML in the same directory as the JSON file
python scripts/generate_html_from_json.py output/report.json

# Generate HTML in a specific directory
python scripts/generate_html_from_json.py output/report.json my_reports/

# Works with any BehaveX JSON report
python scripts/generate_html_from_json.py /path/to/archived/results/report.json
```

**Use Cases:**
- Regenerate HTML reports after template changes
- Create reports from archived test results
- Generate reports in different locations without re-running tests
- Share test results as standalone HTML files

## Requirements

These scripts require BehaveX to be installed and available in the Python path.
