"""
/*
* BehaveX - Agile test wrapper on top of Behave (BDD)
*/

Allure formatter for BehaveX test results.

Summary
Step 1: Install Allure using Homebrew.
Step 2: Run the provided Python script to parse the test results.
Step 3: Generate the Allure report from the parsed results.
Step 4: Serve the Allure report to view it in a web browser.

Steps:

Install Allure: Ensure you have Allure installed on your system. You can use Homebrew to install Allure on macOS.:
* brew install allure

Run the Script: Execute the Python script to parse the report.json file from the output folder. This will generate Allure results in the allure-results directory.
* python3 allure_behavex_report.py

Generate Allure Report: Use the Allure command-line tool to generate the Allure report from the results. This will create the report in the allure-report directory.
* allure serve allure-results
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import uuid
from pathlib import Path

from allure_commons.model2 import (Attachment, Parameter, TestResult,
                                   TestStepResult)
from allure_commons.types import AttachmentType
from allure_commons.utils import now

from behavex.conf_mgr import get_env, get_param
from behavex.outputs.report_utils import get_string_hash


class AllureBehaveXFormatter:
    """Allure formatter for BehaveX test results."""

    # Default output directory for this formatter
    DEFAULT_OUTPUT_DIR = 'allure-results'

    def _get_step_line_from_image(self, filename):
        """Extract step line number from image filename.

        Args:
            filename (str): Image filename in format <scenario_hash>_<5_digits_step_line><5_digits_image_number>

        Returns:
            int: Step line number or None if not found
        """
        try:
            # Split by underscore and get the last part containing line and image numbers
            numbers_part = filename.split('_')[-1]
            # Extract the first 5 digits which represent the step line
            return int(numbers_part[:5])
        except (IndexError, ValueError):
            return None

    def _get_mime_type(self, filename):
        """Get MIME type based on file extension."""
        # Image formats
        if filename.lower().endswith('.png'):
            return "image/png"
        elif filename.lower().endswith(('.jpg', '.jpeg')):
            return "image/jpeg"
        elif filename.lower().endswith('.gif'):
            return "image/gif"
        elif filename.lower().endswith('.svg'):
            return "image/svg+xml"
        elif filename.lower().endswith('.webp'):
            return "image/webp"
        elif filename.lower().endswith('.bmp'):
            return "image/bmp"

        # Document formats
        elif filename.lower().endswith('.pdf'):
            return "application/pdf"
        elif filename.lower().endswith('.doc'):
            return "application/msword"
        elif filename.lower().endswith(('.docx', '.docm')):
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif filename.lower().endswith('.xls'):
            return "application/vnd.ms-excel"
        elif filename.lower().endswith(('.xlsx', '.xlsm')):
            return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        elif filename.lower().endswith('.ppt'):
            return "application/vnd.ms-powerpoint"
        elif filename.lower().endswith(('.pptx', '.pptm')):
            return "application/vnd.openxmlformats-officedocument.presentationml.presentation"

        # Text and data formats
        elif filename.lower().endswith('.txt'):
            return "text/plain"
        elif filename.lower().endswith('.csv'):
            return "text/csv"
        elif filename.lower().endswith('.html'):
            return "text/html"
        elif filename.lower().endswith('.htm'):
            return "text/html"
        elif filename.lower().endswith('.xml'):
            return "application/xml"
        elif filename.lower().endswith('.json'):
            return "application/json"
        elif filename.lower().endswith('.yaml'):
            return "application/x-yaml"
        elif filename.lower().endswith('.yml'):
            return "application/x-yaml"

        # Archive formats
        elif filename.lower().endswith('.zip'):
            return "application/zip"
        elif filename.lower().endswith('.tar'):
            return "application/x-tar"
        elif filename.lower().endswith('.gz'):
            return "application/gzip"
        elif filename.lower().endswith('.7z'):
            return "application/x-7z-compressed"

        # Audio/Video formats
        elif filename.lower().endswith('.mp4'):
            return "video/mp4"
        elif filename.lower().endswith('.webm'):
            return "video/webm"
        elif filename.lower().endswith('.mp3'):
            return "audio/mpeg"
        elif filename.lower().endswith('.wav'):
            return "audio/wav"

        # Logs & code
        elif filename.lower().endswith('.log'):
            return "text/plain"
        elif filename.lower().endswith(('.js', '.py', '.java', '.c', '.cpp', '.cs', '.php', '.rb', '.sh')):
            return "text/plain"

        # Default for unknown types
        else:
            # Use a generic binary format for unknown file types
            # This will cause the browser to offer to download the file
            # rather than trying to display it incorrectly
            return "application/octet-stream"

    def _sanitize_error_message(self, message):
        """Sanitize error message for use as category name.

        Args:
            message (str): Error message

        Returns:
            str: Sanitized message for use as category name
        """
        if not message:
            return "Unknown Error"

        # Get first line or up to 50 chars
        first_line = message.split("\n")[0].strip()
        if len(first_line) > 50:
            first_line = first_line[:47] + "..."

        return first_line or "Unknown Error"

    def _get_package_from_path(self, feature_file_path):
        """Extract package name from feature file path.

        Args:
            feature_file_path (str): Path to the feature file

        Returns:
            str: Package name derived from path
        """
        if not feature_file_path:
            return "default"

        # Normalize path and split into components
        parts = os.path.normpath(feature_file_path).split(os.sep)

        # Find key directory markers like 'features', 'automated', etc.
        key_dirs = ['features', 'automated', 'manual']
        for key_dir in key_dirs:
            if key_dir in parts:
                idx = parts.index(key_dir)
                if idx + 1 < len(parts):
                    # Get subdirectories after the key directory but before the filename
                    package_parts = parts[idx+1:-1]
                    if package_parts:
                        return '.'.join(package_parts)

        # Fallback: use parent directory name
        if len(parts) > 1:
            return parts[-2]

        return "default"

    def _format_table_as_csv(self, table):
        """Format a table as CSV from BehaveX's table format.

        Args:
            table (dict): Dictionary where keys are column headers and values are lists of values

        Returns:
            str: CSV representation of the table
        """
        if not table:
            return ""

        headers = list(table.keys())
        if not headers:
            return ""

        # Get number of rows
        row_count = len(table[headers[0]])

        # Create CSV using StringIO and csv module
        with io.StringIO() as buffer:
            writer = csv.writer(buffer)
            writer.writerow(headers)

            # Write each row
            for row_idx in range(row_count):
                row_values = []
                for header in headers:
                    row_values.append(table[header][row_idx])
                writer.writerow(row_values)

            return buffer.getvalue()

    def _attach_evidence_files(self, test_case, scenario_hash, output_dir):
        """Attach evidence files from the evidence directory to the test case.

        Args:
            test_case (TestResult): The test case to attach evidence to
            scenario_hash (str): The hash identifying the scenario
            output_dir (str): Output directory for Allure results

        Returns:
            TestResult: The updated test case with evidence attachments
        """

        logs_dir = get_env('logs')
        if logs_dir is None:
            # Handle standalone script execution case
            logs_dir = os.path.join(os.path.dirname(output_dir), 'outputs', 'logs')
        evidence_dir = os.path.join(logs_dir, str(scenario_hash), 'evidence')

        if not os.path.exists(evidence_dir):
            return test_case

        # Process all files in the evidence directory
        evidence_files = sorted(os.listdir(evidence_dir))
        # Filter out system files like .DS_Store, Thumbs.db, etc.
        evidence_files = [f for f in evidence_files if not f.startswith('.') and not f == 'Thumbs.db']

        # If there are no valid evidence files, return without attaching anything
        if not evidence_files:
            return test_case

        evidence_attachments = []

        for filename in evidence_files:
            file_path = os.path.join(evidence_dir, filename)
            if os.path.isfile(file_path):
                # In test mode, just print what we would attach
                if test_case is None:
                    continue

                # Get the relative path from the output directory to the evidence file
                # This ensures the file can be found when viewing the report
                try:
                    rel_path = os.path.relpath(file_path, output_dir)
                except ValueError:
                    # If the files are on different drives (Windows), use the absolute path
                    rel_path = file_path

                # Create an attachment object that references the original file
                evidence_attachments.append(
                    Attachment(
                        source=rel_path,
                        name=f"🔍 Evidence: {filename}",
                        type=self._get_mime_type(filename)
                    )
                )

        # If we have evidence files, add them directly to the test case
        if evidence_attachments and test_case is not None:
            # Create a parameter to indicate these are evidence files
            test_case.parameters.append(Parameter(
                name="🔍 Evidence Files",
                value=f"{len(evidence_attachments)} files attached"
            ))

            # Add all evidence attachments directly to the test case
            for attachment in evidence_attachments:
                test_case.attachments.append(attachment)

        return test_case

    def launch_json_formatter(self, json_data):
        """
        Generic method to launch the formatter and process JSON test results.

        Args:
            json_data (dict): Dictionary containing the test results data.
        """
        # Use the LOGS environment variable which is set consistently by the runner
        # This ensures evidence, logs, and allure results are all in the same location
        output_dir = get_env('logs')

        # Fallback if LOGS is not set (for standalone script execution)
        if not output_dir:
            output_dir = os.path.join(get_env('OUTPUT') or 'output', self.DEFAULT_OUTPUT_DIR)

        os.makedirs(output_dir, exist_ok=True)

        # Collect unique error messages for categories
        error_messages = set()

        # Process each feature
        for feature in json_data['features']:
            # Create a container for all scenarios in this feature
            feature_uuid = str(uuid.uuid4())

            # Create the container.json file for the feature suite
            container_data = {
                "uuid": feature_uuid,
                "children": [],  # Will store scenario UUIDs
                "befores": [],
                "afters": []
            }

            # Extract package from feature file path
            feature_file_path = feature.get('filename', '')
            package_name = self._get_package_from_path(feature_file_path)

            for scenario in feature['scenarios']:
                scenario_hash = scenario.get('identifier_hash', get_string_hash(f"{str(feature['filename'])}-{str(scenario['line'])}"))
                container_data["children"].append(scenario_hash)

                test_case = TestResult(uuid=scenario_hash)
                test_case.name = scenario['name']
                test_case.fullName = f"{feature['name']}: {scenario['name']}"
                test_case.historyId = get_string_hash(f"{str(feature['filename'])}-{str(scenario['line'])}")

                # Initialize the labels list
                test_case.labels = []

                # Add basic labels for test organization
                test_case.labels.append({"name": "feature", "value": feature['name']})
                test_case.labels.append({"name": "suite", "value": feature['name']})
                test_case.labels.append({"name": "testClass", "value": feature['name']})
                test_case.labels.append({"name": "testMethod", "value": scenario['name']})
                test_case.labels.append({"name": "framework", "value": "BehaveX"})
                test_case.labels.append({"name": "language", "value": "Python"})

                # Add package label if available
                if package_name:
                    test_case.labels.append({"name": "package", "value": package_name})

                # Process scenario outline parameters
                if 'parameters' in scenario and scenario['parameters']:
                    for name, value in scenario['parameters'].items():
                        test_case.parameters.append(Parameter(name=name, value=value))

                # Process steps and look for failures
                test_error_msg = None  # Store test's error message

                for step in scenario['steps']:
                    allure_step = TestStepResult(
                        name=f"{step['step_type'].capitalize()} {step['name']}"
                    )
                    allure_step.status = step["status"]
                    allure_step.start = step.get("start", now())
                    allure_step.stop = step.get("stop", now())
                    allure_step.line = step.get("line", 0)

                    # Add multiline text as an attachment if present
                    if 'text' in step and step['text'] and step['text'] != 'None':
                        # Create text attachment with step text content
                        text_content = step['text']
                        attachment_source = str(uuid.uuid4())
                        attachment_file = os.path.join(output_dir, attachment_source)
                        with open(attachment_file, 'w') as f:
                            f.write(text_content)

                        # Add the text as an attachment to the step
                        allure_step.attachments.append(
                            Attachment(source=attachment_source,
                                     name="Step Text",
                                     type="text/plain")
                        )

                    # Add table data as parameters if present
                    if 'table' in step and step['table']:
                        # Create CSV formatted table data
                        table_csv = self._format_table_as_csv(step['table'])
                        attachment_source = str(uuid.uuid4())
                        attachment_file = os.path.join(output_dir, attachment_source)
                        with open(attachment_file, 'w') as f:
                            f.write(table_csv)

                        # Add the table as an attachment to the step, following allure-behave's approach
                        allure_step.attachments.append(
                            Attachment(source=attachment_source,
                                     name=".table",
                                     type="text/csv")
                        )

                    if step["status"] in ("failed", "broken"):
                        error_msg = step.get('error_msg', '')
                        if error_msg and not test_error_msg:  # Save first error
                            test_error_msg = error_msg
                            # Add to our collection of unique errors
                            error_messages.add(error_msg)

                        allure_step.statusDetails = {
                            "message": error_msg,
                            "trace": step.get('error_lines', [''])[0]
                        }

                    test_case.steps.append(allure_step)

                # If test failed, add its error as a direct category
                if test_error_msg:
                    # Explicitly mark this test case as a Product Defect
                    test_case.labels.append({"name": "category", "value": "Product Defects"})

                    # Add error details to the test case
                    test_case.statusDetails = {
                        "message": test_error_msg,
                        "flaky": False
                    }

                # Process tags
                package_from_tag = None
                test_thread_already_set = False
                for tag in scenario['tags']:
                    if tag.startswith("epic="):
                        test_case.labels.append({"name": "epic", "value": tag.split("=")[-1]})
                    elif tag.startswith("RC-"):
                        test_case.labels.append({"name": "epic", "value": tag})
                    elif tag.startswith("story="):
                        test_case.labels.append({"name": "story", "value": tag.split("=")[-1]})
                    elif tag.startswith("VPD"):
                        test_case.labels.append({"name": "story", "value": tag})
                    elif tag.startswith("severity="):
                        test_case.labels.append({"name": "severity", "value": tag.split("=")[-1]})
                    elif tag.startswith("author:"):
                        test_case.labels.append({"name": "author", "value": tag.split(":")[-1]})
                    elif tag.startswith("allure.tms:"):
                        test_case.links.append({
                            "type": "tms",
                            "url": tag.split("tms:")[-1],
                            "name": tag.split("tms:")[-1]
                        })
                    elif tag.startswith("allure.issue:"):
                        test_case.links.append({
                            "type": "issue",
                            "url": tag.split("issue:")[-1],
                            "name": tag.split("issue:")[-1]
                        })
                    elif tag.startswith("package="):
                        # Override package from file path with the one from tag
                        package_from_tag = tag.split("=")[-1]
                        # Remove the previous package label
                        test_case.labels = [label for label in test_case.labels if label.get("name") != "package"]
                        # Add the package from tag
                        test_case.labels.append({"name": "package", "value": package_from_tag})
                    elif tag.startswith("allure.label."):
                        label_key, label_value = tag.removeprefix("allure.label.").split(":")
                        if label_key == "thread":
                            test_thread_already_set = True
                        test_case.labels.append({
                            "name": label_key,
                            "value": label_value
                        })
                    else:
                        test_case.labels.append({"name": "tag", "value": tag})
                # Add thread label if not already set and process_id is present
                if "process_id" in scenario.keys() and not test_thread_already_set:
                    test_case.labels.append({"name": "thread", "value": scenario["process_id"]})
                # Add scenario timing
                test_case.start = scenario.get("start", now())
                test_case.stop = scenario.get("stop", now())
                test_case.status = scenario['status']

                # Process scenario logs as attachment
                if get_param('formatter_attach_logs'):
                    scenario_hash = scenario.get('identifier_hash', get_string_hash(f"{str(feature['filename'])}-{str(scenario['line'])}"))
                    logs_dir_for_log = get_env('logs')
                    if logs_dir_for_log is None:
                        # Handle standalone script execution case
                        logs_dir_for_log = os.path.join(os.path.dirname(output_dir), 'outputs', 'logs')
                    log_path = os.path.join(logs_dir_for_log, str(scenario_hash), 'scenario.log')
                    if os.path.exists(log_path):
                        # Use relative path for the source if possible to avoid duplication
                        rel_path = os.path.relpath(log_path, output_dir) if output_dir in log_path else log_path
                        test_case.attachments.append(
                            Attachment(source=rel_path,
                                     name="scenario.log",
                                     type="text/plain")
                        )

                # Process evidence files
                test_case = self._attach_evidence_files(test_case, scenario_hash, output_dir)

                # Process screenshots
                scenario_images = []
                for filename in os.listdir(output_dir):
                    if filename.startswith(str(scenario_hash)) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        scenario_images.append(filename)

                # Sort images by name to ensure consistent numbering
                scenario_images.sort()

                # Add screenshots as attachments
                screenshot_counter = {}  # Keep track of screenshots per step
                for filename in scenario_images:
                    step_line = self._get_step_line_from_image(filename)
                    if step_line is not None:
                        # Find matching step by line number
                        for step in test_case.steps:
                            if step_line == step.line:
                                # Initialize counter for this step if not exists
                                if step_line not in screenshot_counter:
                                    screenshot_counter[step_line] = 1
                                else:
                                    screenshot_counter[step_line] += 1

                                # Create friendly name
                                friendly_name = f"step_image_{screenshot_counter[step_line]}"

                                # Add image as attachment to the step
                                step.attachments.append(
                                    Attachment(source=filename,
                                             name=friendly_name,
                                             type=self._get_mime_type(filename))
                                )
                                break

                # Save test result
                test_case_path = os.path.join(output_dir, f"{scenario_hash}-result.json")
                test_case_dict = {
                    "uuid": test_case.uuid,
                    "historyId": test_case.historyId,
                    "name": test_case.name,
                    "fullName": test_case.fullName,
                    "status": test_case.status,
                    "statusDetails": test_case.statusDetails if hasattr(test_case, 'statusDetails') else {},
                    "labels": test_case.labels,
                    "links": test_case.links if hasattr(test_case, 'links') else [],
                    "steps": [{
                        "name": step.name,
                        "status": step.status,
                        "start": step.start,
                        "stop": step.stop,
                        "statusDetails": getattr(step, 'statusDetails', {}),
                        "attachments": [{
                            "name": attachment.name,
                            "source": attachment.source,
                            "type": attachment.type
                        } for attachment in (getattr(step, 'attachments', []) or [])]
                    } for step in test_case.steps],
                    "attachments": [{
                        "name": attachment.name,
                        "source": attachment.source,
                        "type": attachment.type
                    } for attachment in test_case.attachments],
                    "parameters": [{"name": p.name, "value": p.value} for p in test_case.parameters] if hasattr(test_case, 'parameters') else [],
                    "start": test_case.start,
                    "stop": test_case.stop
                }

                # Add hierarchical labels for better organization in Allure report
                if feature_file_path:
                    # Create hierarchical representation from feature file path
                    hierarchical_package = feature_file_path.replace("/", ".")
                    if hasattr(str, 'removesuffix'):  # Python 3.9+
                        hierarchical_package = hierarchical_package.removesuffix('.feature')
                    elif hierarchical_package.endswith('.feature'):
                        hierarchical_package = hierarchical_package[:-len('.feature')]

                    # Remove existing package and suite labels to avoid duplication
                    test_case_dict["labels"] = [label for label in test_case_dict["labels"]
                                               if label.get("name") != "package" and label.get("name") != "suite"]

                    # Add new hierarchical labels, skipping the feature filename level
                    test_case_dict["labels"].append({"name": "package", "value": hierarchical_package})
                    test_case_dict["labels"].append({"name": "parentSuite", "value": os.path.dirname(feature_file_path)})
                    test_case_dict["labels"].append({"name": "suite", "value": feature['name']})

                with open(test_case_path, "w") as f:
                    json.dump(test_case_dict, f, default=str)

            # Save the container file for the feature
            container_path = os.path.join(output_dir, f"{feature_uuid}-container.json")
            with open(container_path, "w") as f:
                json.dump(container_data, f, default=str)

        # Create categories.json using a different approach that forces nesting
        categories = [
            # The Product Defects top-level category that captures all failed tests
            {
                "name": "Product Defects",
                "matchedStatuses": ["failed"]
            },
            # Add a separate category for broken tests
            {
                "name": "Broken Tests",
                "matchedStatuses": ["broken"]
            }
        ]

        # Create a simpler "categories.json" format that guarantees proper nesting
        # This is the minimal format that works reliably with Allure
        with open(os.path.join(output_dir, "categories.json"), "w") as f:
            json.dump(categories, f, indent=2)

        # Only create this file if we have error messages to categorize
        if error_messages:
            # Create an environment-categories.json file that defines the subcategories
            # This separates the category definitions to avoid conflicts
            env_categories = []

            # Add subcategories for each unique error
            for error_msg in error_messages:
                clean_message = self._sanitize_error_message(error_msg)

                # Skip duplicates
                if any(cat.get("name") == clean_message for cat in env_categories):
                    continue

                env_categories.append({
                    "name": clean_message,
                    "matchedStatuses": ["failed"],
                    "messageRegex": ".*" + re.escape(clean_message) + ".*",
                    "parentName": "Product Defects"
                })

            # Write the environment-based categories file
            with open(os.path.join(output_dir, "environment-categories.json"), "w") as f:
                json.dump(env_categories, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Parse BehaveX report.json into Allure format')
    parser.add_argument('--report-path',
                       type=str,
                       default=os.path.join(Path(__file__).resolve().parent, "output", "report.json"),
                       help='Path to the report.json file (default: ./output/report.json)')

    args = parser.parse_args()

    formatter = AllureBehaveXFormatter()

    try:
        with open(args.report_path) as f:
            formatter.launch_json_formatter(json.load(f))
    except FileNotFoundError:
        print(f"Error: Could not find report file at {args.report_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in report file at {args.report_path}")
        sys.exit(1)



if __name__ == "__main__":
    # you can run this script from the command line like this:
    # pipenv run python3 /behavex/outputs/formatters/allure_behavex_formatter.py --report-path ./output/report.json
    #
    # Also, you can generate the report from the command line like this:
    # allure generate output/allure-results --output ./output/allure-report --clean --single-file
    main()
