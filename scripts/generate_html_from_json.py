#!/usr/bin/env python3
"""
BehaveX HTML Report Generator

Utility script to generate HTML report from existing report.json file.
This is useful when you want to regenerate the HTML report without re-running tests.

Usage: python generate_html_from_json.py [path_to_report.json] [output_directory]

Examples:
    # Generate HTML in the same directory as the JSON file
    python generate_html_from_json.py output/report.json

    # Generate HTML in a specific directory
    python generate_html_from_json.py output/report.json my_reports/

    # Works with any BehaveX JSON report
    python generate_html_from_json.py /path/to/old_execution/report.json
"""
import json
import os
import sys
import time
from pathlib import Path

# Add current directory to path so we can import behavex modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from behavex.conf_mgr import set_env
from behavex.global_vars import global_vars
from behavex.outputs import report_html


def generate_html_from_json(json_file_path, output_dir=None):
    """Generate HTML report from existing JSON report file."""

    # Set default output directory if not provided
    if output_dir is None:
        output_dir = os.path.dirname(json_file_path) or 'output'

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Set environment variables that BehaveX expects (keys are stored in lowercase)
    set_env('output', output_dir)
    set_env('temp', os.path.join(output_dir, 'temp'))
    set_env('logs', os.path.join(output_dir, 'outputs', 'logs'))

    # Create necessary directories
    os.makedirs(os.path.join(output_dir, 'outputs', 'bootstrap', 'css'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'outputs', 'bootstrap', 'manifest'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'outputs', 'logs'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, 'temp'), exist_ok=True)

    # Load the JSON report first to get real execution times
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    # Calculate real execution start and end times from scenario data
    scenario_start_times = []
    scenario_end_times = []

    for feature in json_data.get('features', []):
        for scenario in feature.get('scenarios', []):
            if 'start' in scenario:
                start_time = scenario['start']
                # Convert milliseconds to seconds if needed
                if start_time > 1000000000000:  # milliseconds
                    start_time = start_time / 1000
                scenario_start_times.append(start_time)

            if 'stop' in scenario:
                stop_time = scenario['stop']
                # Convert milliseconds to seconds if needed
                if stop_time > 1000000000000:  # milliseconds
                    stop_time = stop_time / 1000
                scenario_end_times.append(stop_time)

    # Set global execution times from actual scenario data
    if scenario_start_times and scenario_end_times:
        global_vars._execution_start_time = min(scenario_start_times)
        global_vars._execution_end_time = max(scenario_end_times)
    else:
        # Fallback to current time if no scenario data available
        global_vars._execution_start_time = time.time() - 60
        global_vars._execution_end_time = time.time()

    try:
        # Generate HTML report (json_data already loaded above)
        print(f"Generating HTML report from {json_file_path}...")
        report_html.generate_report(json_data)

        html_path = os.path.join(output_dir, 'report.html')
        print(f"HTML report generated successfully: {html_path}")

        return html_path

    except FileNotFoundError:
        print(f"Error: JSON file not found: {json_file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {json_file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error generating HTML report: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main entry point for command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python generate_html_from_json.py <path_to_report.json> [output_directory]")
        print("\nExamples:")
        print("  python generate_html_from_json.py output/report.json")
        print("  python generate_html_from_json.py output/report.json my_reports/")
        sys.exit(1)

    json_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(json_file):
        print(f"Error: File not found: {json_file}")
        sys.exit(1)

    result = generate_html_from_json(json_file, output_dir)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
