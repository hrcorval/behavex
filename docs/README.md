[![Downloads](https://static.pepy.tech/badge/behavex)](https://pepy.tech/project/behavex)
[![PyPI version](https://badge.fury.io/py/behavex.svg)](https://badge.fury.io/py/behavex)
[![Python Versions](https://img.shields.io/pypi/pyversions/behavex.svg)](https://pypi.org/project/behavex/)
[![Dependency Status](https://img.shields.io/librariesio/github/hrcorval/behavex)](https://libraries.io/github/hrcorval/behavex)
[![License](https://img.shields.io/github/license/hrcorval/behavex.svg)](https://github.com/hrcorval/behavex/blob/main/LICENSE)
[![Build Status](https://github.com/hrcorval/behavex/actions/workflows/python-package.yml/badge.svg)](https://github.com/hrcorval/behavex/actions)
[![GitHub last commit](https://img.shields.io/github/last-commit/hrcorval/behavex.svg)](https://github.com/hrcorval/behavex/commits/main)

# BehaveX Documentation

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
- [Installation Instructions](#installation-instructions)
- [Execution Instructions](#execution-instructions)
- [Constraints](#constraints)
- [Supported Behave Arguments](#supported-behave-arguments)
- [Specific Arguments from BehaveX](#specific-arguments-from-behavex)
- [Parallel Test Executions](#parallel-test-executions)
- [Test Execution Reports](#test-execution-reports)
- [Attaching Images and Evidence](#attaching-images-and-evidence)
- [Test Logs and Metrics](#test-logs-and-metrics)
- [Muting Test Scenarios](#muting-test-scenarios)
- [Handling Failing Scenarios](#handling-failing-scenarios)
- [FAQs](#faqs)
- [Show Your Support](#show-your-support)

## Introduction

**BehaveX** is a BDD testing solution designed to enhance your Behave-based testing workflow by providing additional features and performance improvements. It's particularly beneficial in the following scenarios:

- **Accelerating test execution**: Significantly reduce test run times through parallel execution by feature or scenario.
- **Enhancing test reporting**: Generate comprehensive and visually appealing HTML and JSON reports for in-depth analysis and integration with other tools.
- **Improving test visibility**: Provide detailed evidence, such as screenshots and logs, essential for understanding test failures and successes.
- **Optimizing test automation**: Utilize features like test retries, test muting, and performance metrics for efficient test maintenance and analysis.
- **Managing complex test suites**: Handle large test suites with advanced features for organization, execution, and reporting.

## Features

BehaveX provides the following features:

- **Parallel Test Executions**: Execute tests using multiple processes, either by feature or by scenario.
- **Enhanced Reporting**: Generate friendly HTML and JSON reports that can be exported and integrated with third-party tools.
- **Evidence Collection**: Include images/screenshots and additional evidence in the HTML report.
- **Test Logs**: Automatically compile logs generated during test execution into individual log reports for each scenario.
- **Test Muting**: Add the `@MUTE` tag to test scenarios to execute them without including them in JUnit reports.
- **Execution Metrics**: Generate metrics in the HTML report for the executed test suite, including Automation Rate and Pass Rate.
- **Dry Runs**: Perform dry runs to see the full list of scenarios in the HTML report without executing the tests.
- **Auto-Retry for Failing Scenarios**: Use the `@AUTORETRY` tag to automatically re-execute failing scenarios.

![Test Execution Report](https://github.com/hrcorval/behavex/blob/master/img/html_test_report.png?raw=true)
![Test Execution Report](https://github.com/hrcorval/behavex/blob/master/img/html_test_report_2.png?raw=true)
![Test Execution Report](https://github.com/hrcorval/behavex/blob/master/img/html_test_report_3.png?raw=true)

## Installation Instructions

To install BehaveX, execute the following command:

```bash
pip install behavex
```

## Execution Instructions

Execute BehaveX in the same way as Behave from the command line, using the `behavex` command. Here are some examples:

- **Run scenarios tagged as `TAG_1` but not `TAG_2`:**
  ```bash
  behavex -t=@TAG_1 -t=~@TAG_2
  ```

- **Run scenarios tagged as `TAG_1` or `TAG_2`:**
  ```bash
  behavex -t=@TAG_1,@TAG_2
  ```

- **Run scenarios tagged as `TAG_1` using 4 parallel processes:**
  ```bash
  behavex -t=@TAG_1 --parallel-processes=4 --parallel-scheme=scenario
  ```

- **Run scenarios located at specific folders using 2 parallel processes:**
  ```bash
  behavex features/features_folder_1 features/features_folder_2 --parallel-processes=2
  ```

- **Run scenarios from a specific feature file using 2 parallel processes:**
  ```bash
  behavex features_folder_1/sample_feature.feature --parallel-processes=2
  ```

- **Run scenarios tagged as `TAG_1` from a specific feature file using 2 parallel processes:**
  ```bash
  behavex features_folder_1/sample_feature.feature -t=@TAG_1 --parallel-processes=2
  ```

- **Run scenarios located at specific folders using 2 parallel processes:**
  ```bash
  behavex features/feature_1 features/feature_2 --parallel-processes=2
  ```

- **Run scenarios tagged as `TAG_1`, using 5 parallel processes executing a feature on each process:**
  ```bash
  behavex -t=@TAG_1 --parallel-processes=5 --parallel-scheme=feature
  ```

- **Perform a dry run of the scenarios tagged as `TAG_1`, and generate the HTML report:**
  ```bash
  behavex -t=@TAG_1 --dry-run
  ```

- **Run scenarios tagged as `TAG_1`, generating the execution evidence into a specific folder:**
  ```bash
  behavex -t=@TAG_1 -o=execution_evidence
  ```

## Constraints

- BehaveX is currently implemented on top of Behave **v1.2.6**, and not all Behave arguments are yet supported.
- The parallel execution implementation is based on concurrent Behave processes. Hooks in the `environment.py` module will be executed in each parallel process.

## Supported Behave Arguments

- no_color
- color
- define
- exclude
- include
- no_snippets
- no_capture
- name
- capture
- no_capture_stderr
- capture_stderr
- no_logcapture
- logcapture
- logging_level
- summary
- quiet
- stop
- tags
- tags-help

**Important**: Some arguments do not apply when executing tests with more than one parallel process, such as **stop** and **color**.

## Specific Arguments from BehaveX

- **output-folder** (-o or --output-folder): Specifies the output folder for execution reports (JUnit, HTML, JSON).
- **dry-run** (-d or --dry-run): Performs a dry-run by listing scenarios in the output reports.
- **parallel-processes** (--parallel-processes): Specifies the number of parallel Behave processes.
- **parallel-scheme** (--parallel-scheme): Performs parallel test execution by [scenario|feature].
- **show-progress-bar** (--show-progress-bar): Displays a progress bar in the console during parallel test execution.

## Parallel Test Executions

BehaveX manages concurrent executions of Behave instances in multiple processes. You can perform parallel test executions by feature or scenario.

### Examples:
```bash
behavex --parallel-processes=3
behavex -t=@<TAG> --parallel-processes=3
behavex -t=@<TAG> --parallel-processes=2 --parallel-scheme=scenario
behavex -t=@<TAG> --parallel-processes=5 --parallel-scheme=feature
behavex -t=@<TAG> --parallel-processes=5 --parallel-scheme=feature --show-progress-bar
```

## Test Execution Reports

### HTML Report
A friendly test execution report containing information related to test scenarios, execution status, evidence, and metrics. Available at:
```bash
<output_folder>/report.html
```

### JSON Report
Contains information about test scenarios and execution status. Available at:
```bash
<output_folder>/report.json
```

### JUnit Report
One JUnit file per feature, available at:
```bash
<output_folder>/behave/*.xml
```

## Attaching Images and Evidence

You can attach images or screenshots to the HTML report. Use the following methods:

### Example 1: Attaching an Image File
```python
from behavex_images import image_attachments

@given('I take a screenshot from current page')
def step_impl(context):
    image_attachments.attach_image_file(context, 'path/to/image.png')
```

### Example 2: Attaching an Image Binary
```python
from behavex_images import image_attachments
from behavex_images.image_attachments import AttachmentsCondition

def before_all(context):
    image_attachments.set_attachments_condition(context, AttachmentsCondition.ONLY_ON_FAILURE)

def after_step(context, step):
    image_attachments.attach_image_binary(context, selenium_driver.get_screenshot_as_png())
```

## Test Logs and Metrics

The HTML report provides test execution logs per scenario. Metrics include:

- Automation Rate
- Pass Rate
- Steps execution counter and average execution time

## Muting Test Scenarios

To mute failing test scenarios, add the `@MUTE` tag. This allows the test to run without being included in JUnit reports.

## Handling Failing Scenarios

### @AUTORETRY Tag
This tag can be used for flaky scenarios or when the testing infrastructure is not stable. The `@AUTORETRY` tag can be applied to any scenario or feature, and it is used to automatically re-execute the test scenario when it fails.

### Rerun All Failed Scenarios
Whenever you perform an automated test execution and there are failing scenarios, the **failing_scenarios.txt** file will be created in the execution output folder. This file allows you to run all failing scenarios again.

To rerun failing scenarios, execute:
```bash
behavex -rf=./<OUTPUT_FOLDER>/failing_scenarios.txt
```
or
```bash
behavex --rerun-failures=./<OUTPUT_FOLDER>/failing_scenarios.txt
```

To avoid overwriting the previous test report, provide a different output folder using the **-o** or **--output-folder** argument.

## FAQs

- **How do I install BehaveX?**
  - Use `pip install behavex`.

- **What is the purpose of the `@AUTORETRY` tag?**
  - It automatically re-executes failing scenarios.

- **How can I mute a test scenario?**
  - Add the `@MUTE` tag to the scenario.

## Show Your Support

If you find this project helpful, please give it a star! Your support helps us gain visibility and motivates us to continue improving the project.

Thank you for your support!
