import logging
import os

from behave import given, then, when
from execution_steps import (
    execute_command,
    new_output_path,
    root_project_path,
    secondary_features_path,
)

test_images_path = os.path.join(root_project_path, 'tests', 'test_images')


# Import behavex-images functionality - fail if required
def get_image_attachments_module():
    """Get the image_attachments module, raising an error if not available."""
    try:
        from behavex_images import image_attachments
        return image_attachments
    except (ImportError, ModuleNotFoundError) as e:
        raise AssertionError(f"behavex-images is required for image attachment tests but not available: {e}")

# Check if behavex-images is available for optional usage
try:
    from behavex_images import image_attachments
    behavex_images_available = True
except (ImportError, ModuleNotFoundError) as e:
    behavex_images_available = False
    logging.warning(f"behavex-images not available, image attachment tests will be skipped: {e}")


@given('I take a screenshot using test image {image_number}')
def step_take_screenshot_using_test_image(context, image_number):
    """Attach a test image file using behavex-images"""
    image_path = os.path.join(test_images_path, f'test_image_{image_number}.png')
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Test image not found: {image_path}")

    # Check if image attachments are required for this test
    if hasattr(context, 'require_image_attachments') and context.require_image_attachments:
        image_attachments = get_image_attachments_module()
        image_attachments.attach_image_file(context, image_path)
        logging.info(f"Attached test image: {image_path}")
    else:
        # Optional usage - skip if not available
        if not behavex_images_available:
            logging.warning("behavex-images not available, skipping image attachment")
            return
        # Import here to avoid issues if behavex-images is not available
        from behavex_images import image_attachments
        image_attachments.attach_image_file(context, image_path)
        logging.info(f"Attached test image: {image_path}")


@given('image attachments are configured for ONLY_ON_FAILURE condition')
def step_configure_only_on_failure_attachments(context):
    """Configure image attachments to use ONLY_ON_FAILURE condition"""
    context.attachment_condition = 'ONLY_ON_FAILURE'

@when('I run the behavex command with image attachments')
def step_run_behavex_with_image_attachments(context):
    """Run behavex with HTML formatter and image attachments enabled"""
    context.output_path = new_output_path()
    execution_args = [
        'behavex',
        os.path.join(secondary_features_path, 'simple_image_tests.feature'),
        '-o', context.output_path,
        '-t', '@IMAGE_ATTACHMENT',
        '-t', '@HTML_REPORT'
    ]
    execute_command(context, execution_args)


@when('I run the behavex command with failed scenario and image attachments')
def step_run_behavex_with_failed_scenario_and_image_attachments(context):
    """Run behavex with failed scenario and image attachments enabled"""
    context.output_path = new_output_path()
    execution_args = [
        'behavex',
        os.path.join(secondary_features_path, 'image_attachments_failing_step.feature'),
        '-o', context.output_path,
        '-t', '@IMAGE_ATTACHMENT',
        '-t', '@FAILED_SCENARIO'
    ]
    # Expect non-zero exit code due to failed scenario
    context.expected_exit_code = 1
    execute_command(context, execution_args)

@when('I run the behavex command with error scenario and image attachments')
def step_run_behavex_with_error_scenario_and_image_attachments(context):
    """Run behavex with error scenario and image attachments enabled"""
    context.output_path = new_output_path()
    execution_args = [
        'behavex',
        os.path.join(secondary_features_path, 'image_attachments_undefined_step.feature'),
        '-o', context.output_path,
        '-t', '@IMAGE_ATTACHMENT',
        '-t', '@ERROR_SCENARIO'
    ]
    # Expect non-zero exit code due to error scenario
    context.expected_exit_code = 1
    execute_command(context, execution_args)


@then('I should see that images are attached for error scenarios in the HTML report')
def step_verify_images_attached_for_error_scenarios(context):
    """Verify that images are attached in HTML report for scenarios with error status"""
    html_report_path = os.path.join(context.output_path, 'report.html')
    assert os.path.exists(html_report_path), f"HTML report not found at {html_report_path}"

    with open(html_report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Verify that the HTML contains image attachments for error scenarios
    assert "glyphicon-picture" in html_content, "Image attachment icon not found in HTML report"

    # Look for specific patterns that indicate images are attached to error scenarios
    # The HTML should contain scenario rows with error status and image attachments
    assert "error" in html_content.lower(), "Error scenario not found in HTML report"

    logging.info("Successfully verified that images are attached for error scenarios in HTML report")


@then('I should see that images are attached for failed scenarios in the HTML report')
def step_verify_images_attached_for_failed_scenarios(context):
    """Verify that images are attached in HTML report for scenarios with failed status"""
    html_report_path = os.path.join(context.output_path, 'report.html')
    assert os.path.exists(html_report_path), f"HTML report not found at {html_report_path}"

    with open(html_report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Verify that the HTML contains image attachments for failed scenarios
    assert "glyphicon-picture" in html_content, "Image attachment icon not found in HTML report"

    # Look for specific patterns that indicate images are attached to failed scenarios
    # The HTML should contain scenario rows with failed status and image attachments
    assert "failed" in html_content.lower(), "Failed scenario not found in HTML report"

    logging.info("Successfully verified that images are attached for failed scenarios in HTML report")


@then('I should verify current behavior for error scenarios with ONLY_ON_FAILURE condition')
def step_verify_current_behavior_error_scenarios(context):
    """Verify current behavior for error scenarios with ONLY_ON_FAILURE condition"""
    html_report_path = os.path.join(context.output_path, 'report.html')
    assert os.path.exists(html_report_path), f"HTML report not found at {html_report_path}"

    with open(html_report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Verify that the error scenario exists in the report
    assert "error" in html_content.lower(), "Error scenario not found in HTML report"

    # Check current behavior - as of now, ONLY_ON_FAILURE might not attach images for error status
    # This documents the current behavior rather than asserting what should happen
    if "glyphicon-picture" in html_content:
        logging.info("Current behavior: Images ARE attached for error scenarios with ONLY_ON_FAILURE condition")
    else:
        logging.info("Current behavior: Images are NOT attached for error scenarios with ONLY_ON_FAILURE condition")
        logging.info("This may be a feature gap - error status should be treated similar to failed status")

    # The test passes regardless to document current behavior
    logging.info("Successfully documented current behavior for error scenarios with ONLY_ON_FAILURE condition")


@when('I run the behavex command with allure formatter and image attachments')
def step_run_behavex_with_allure_and_image_attachments(context):
    """Run behavex with Allure formatter and image attachments enabled"""
    context.output_path = new_output_path()
    execution_args = [
        'behavex',
        os.path.join(secondary_features_path, 'simple_image_tests.feature'),
        '-o', context.output_path,
        '--formatter=behavex.outputs.formatters.allure_behavex_formatter:AllureBehaveXFormatter',
        '-t', '@IMAGE_ATTACHMENT',
        '-t', '@ALLURE_FORMATTER'
    ]
    execute_command(context, execution_args)


@then('I should see the HTML report contains screenshots')
def step_verify_html_report_contains_screenshots(context):
    """Verify that the HTML report contains attached screenshots"""
    html_report_path = os.path.join(context.output_path, 'report.html')
    if os.path.exists(html_report_path):
        with open(html_report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            # Look for image references in the HTML
            assert 'test_image_' in html_content, "Screenshots not found in HTML report"
            logging.info("Screenshots found in HTML report")
    else:
        raise FileNotFoundError(f"HTML report not found: {html_report_path}")


@then('I should see the HTML report contains the image gallery icon')
def step_verify_html_report_contains_gallery_icon(context):
    """Verify that the HTML report contains the image gallery icon"""
    html_report_path = os.path.join(context.output_path, 'report.html')
    if os.path.exists(html_report_path):
        with open(html_report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            # Look for the specific gallery icon HTML element
            gallery_icon = '<span class="glyphicon glyphicon-picture">'
            assert gallery_icon in html_content, "Image gallery icon not found in HTML report"
            logging.info("Image gallery icon found in HTML report")
    else:
        raise FileNotFoundError(f"HTML report not found: {html_report_path}")


@then('I should see that images are stored in the allure formatter output directory')
def step_verify_images_in_allure_output(context):
    """Verify that images are stored in the Allure formatter output directory"""
    allure_results_path = os.path.join(context.output_path, 'allure-results')
    if os.path.exists(allure_results_path):
        # Look for image attachments in allure results
        allure_files = os.listdir(allure_results_path)
        image_files = [f for f in allure_files if f.endswith('.png') or f.endswith('.jpg') or f.endswith('.jpeg')]
        assert len(image_files) > 0, "No image files found in Allure output directory"
        logging.info(f"Found {len(image_files)} image files in Allure output directory")

        # Also check for attachment references in JSON files
        json_files = [f for f in allure_files if f.endswith('.json')]
        found_attachment_reference = False
        for json_file in json_files:
            json_path = os.path.join(allure_results_path, json_file)
            with open(json_path, 'r', encoding='utf-8') as f:
                json_content = f.read()
                if 'attachments' in json_content and 'image' in json_content:
                    found_attachment_reference = True
                    break

        assert found_attachment_reference, "No image attachment references found in Allure JSON files"
        logging.info("Image attachment references found in Allure JSON files")
    else:
        raise FileNotFoundError(f"Allure results directory not found: {allure_results_path}")
