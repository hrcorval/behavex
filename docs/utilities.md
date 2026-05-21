# Utilities

## HTML Report Generator

Generate HTML reports from existing `report.json` files without re-running tests:

```bash
# Generate HTML in the same directory as the JSON file
python scripts/generate_html_from_json.py output/report.json

# Generate HTML in a specific directory
python scripts/generate_html_from_json.py output/report.json my_reports/

# Works with any BehaveX JSON report
python scripts/generate_html_from_json.py /path/to/archived_run/report.json
```

Useful when you need to:
- Regenerate HTML reports after template or style changes
- Create reports from archived test results
- Generate reports in a different location without re-running tests
