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

import json
import os
import uuid
from datetime import datetime
from pathlib import Path

from allure_commons.model2 import (Attachment, Parameter, TestResult,
                                   TestStepResult)
from allure_commons.types import AttachmentType
from allure_commons.utils import now

from behavex.conf_mgr import get_env
from behavex.outputs.formatter_manager import FormatterManager
from behavex.outputs.report_utils import get_string_hash


class AllureBehaveXFormatter:
    """Allure formatter for BehaveX test results."""

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
        if filename.lower().endswith('.png'):
            return "image/png"
        elif filename.lower().endswith('.gif'):
            return "image/gif"
        else:
            return "image/jpeg"

    def parse_json_to_allure(self, json_data):
        """
        Parses the JSON report data and converts it into Allure-compatible results.

        Args:
            json_data (dict): Dictionary containing the test results data.

        Returns:
            None
        """
        output_dir = FormatterManager.get_formatter_output_dir()
        if not output_dir:
            output_dir = os.path.join(get_env('OUTPUT'), 'allure-results')

        os.makedirs(output_dir, exist_ok=True)

        for feature in json_data['features']:
            for scenario in feature['scenarios']:
                test_case = TestResult(uuid=scenario["id_hash"])
                test_case.name = scenario['name']
                test_case.fullName = scenario['name']

                # Use the stored identifier hash
                scenario_hash = scenario.get('identifier_hash', get_string_hash(f"{str(feature['filename'])}-{str(scenario['line'])}"))

                # Add scenario logs as attachment
                log_path = os.path.join(get_env('logs'), str(scenario_hash), 'scenario.log')
                if os.path.exists(log_path):
                    with open(log_path, 'r') as f:
                        log_content = f.read()
                        attachment_source = str(uuid.uuid4())
                        test_case.attachments.append(
                            Attachment(name="scenario.log",
                                     source=attachment_source,
                                     type="text/plain")
                        )
                        # Write attachment content to a file in allure results
                        attachment_file = os.path.join(output_dir, attachment_source)
                        with open(attachment_file, 'w') as f:
                            f.write(log_content)

                # Create steps first
                steps_with_lines = []
                for step in scenario['steps']:
                    allure_step = TestStepResult(name=step["step_type"].capitalize() + " " + step["name"])
                    allure_step.status = step["status"]
                    allure_step.start = step["start"] if "start" in step else now()
                    allure_step.stop = step["stop"] if "stop" in step else now()

                    if step["status"] in ("failed", "broken"):
                        allure_step.statusDetails = {"message": step['error_msg'],
                                                     "trace": step['error_lines'][0]}

                    # Store step line number for image matching
                    line_number = step.get('line', 0)
                    steps_with_lines.append((allure_step, line_number))
                    test_case.steps.append(allure_step)

                # First, collect and sort all images for this scenario
                scenario_images = []
                for filename in os.listdir(output_dir):
                    if filename.startswith(str(scenario_hash)) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        scenario_images.append(filename)

                # Sort images by name to ensure consistent numbering
                scenario_images.sort()

                # Add screenshots as attachments - using existing images with scenario hash prefix
                screenshot_counter = {}  # Keep track of screenshots per step
                for filename in scenario_images:
                    step_line = self._get_step_line_from_image(filename)
                    if step_line is not None:
                        # Find matching step by line number
                        for allure_step, line_number in steps_with_lines:
                            if line_number == step_line:
                                # Initialize counter for this step if not exists
                                if line_number not in screenshot_counter:
                                    screenshot_counter[line_number] = 1
                                else:
                                    screenshot_counter[line_number] += 1

                                # Create friendly name
                                friendly_name = f"step_image_{screenshot_counter[line_number]}"

                                # Add image as attachment to the step
                                allure_step.attachments.append(
                                    Attachment(name=friendly_name,
                                             source=filename,  # Keep original filename as source
                                             type=self._get_mime_type(filename))
                                )
                                break

                if scenario["status"] in ("failed", "broken"):
                    test_case.statusDetails = {"message": scenario['error_msg'][0],
                                               "trace": scenario['error_lines'][0]}
                for tag in scenario['tags']:
                    if "epic" in tag:
                        test_case.labels.append({"name": "epic", "value": tag.split("=")[-1]}),
                    elif "author" in tag:
                        test_case.labels.append({"name": "author", "value": tag.split(":")[-1]}),
                    elif "allure.tms" in tag:
                        test_case.links.append(
                            {"type": "tms", "url": tag.split("tms:")[-1], "name": tag.split("tms:")[-1]}),
                    elif "allure.issue" in tag:
                        test_case.links.append(
                            {"type": "issue", "url": tag.split("issue:")[-1], "name": tag.split("issue:")[-1]}),
                    elif tag in ("normal", "trivial", "minor", "critical", "blocker"):
                        test_case.labels.append({"name": "severity", "value": tag}),
                    else:
                        test_case.labels.append({"name": "tag", "value": tag})

                if scenario.get('parameters'):
                    for param in scenario['parameters']:
                        test_case.parameters.append(Parameter(name=param['name'], value=param['value']))

                test_case.start = scenario["start"] if "start" in scenario else now()
                test_case.stop = scenario["stop"] if "stop" in scenario else now()
                test_case.status = scenario['status']

                # Create test case dictionary with step attachments
                steps_json = []
                for step in test_case.steps:
                    step_dict = {
                        "name": step.name,
                        "status": step.status,
                        "start": step.start,
                        "stop": step.stop,
                        "statusDetails": step.statusDetails if hasattr(step, 'statusDetails') else {},
                        "attachments": []
                    }

                    # Add step attachments
                    if hasattr(step, 'attachments'):
                        for attachment in step.attachments:
                            step_dict["attachments"].append({
                                "name": attachment.name,
                                "source": attachment.source,
                                "type": attachment.type
                            })

                    steps_json.append(step_dict)

                test_case_dict = {
                    "name": test_case.name,
                    "status": test_case.status,
                    "steps": steps_json,
                    "start": test_case.start,
                    "stop": test_case.stop,
                    "uuid": test_case.uuid,
                    "historyId": test_case.historyId,
                    "fullName": test_case.fullName,
                    "labels": [item for item in test_case.labels],
                    "attachments": [{
                        "name": attachment.name,
                        "source": attachment.source,
                        "type": attachment.type
                    } for attachment in test_case.attachments]
                }
                test_case_dict["labels"].append({"name": "feature", "value": feature['name']})
                test_case_dict["labels"].append({"name": "framework", "value": "BehaveX"})
                test_case_dict["labels"].append({"name": "language", "value": "Python"})

                path = os.path.join(output_dir, f"{uuid.uuid4()}-result.json")
                json_object = json.dumps(test_case_dict, default=str)
                with open(path, "w") as outfile:
                    outfile.write(json_object)


if __name__ == "__main__":
    # Update the path information to point to the report.json file generated in test execution
    path = os.path.join(Path(__file__).resolve().parent, "output", "report.json")
    formatter = AllureBehaveXFormatter()
    formatter.parse_json_to_allure(json.load(open(path)))
