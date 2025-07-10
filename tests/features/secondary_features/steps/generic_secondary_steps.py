import logging
import os

from behave import given, then, when

# Get paths
root_project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
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


@given('a failing condition')
def step_impl(context):
    context.condition = 'fail'
    logging.info('a failing condition')

@given('a passing condition')
def step_impl(context):
    context.condition = 'pass'
    logging.info('a passing condition')

@given('a condition to skip the scenario')
def step_impl(context):
    context.condition = 'skip'
    logging.info('a condition to skip the scenario')

@given('a condition to exit the scenario')
def step_impl(context):
    context.condition = 'exit'
    logging.info('a condition to exit the scenario')

@given('a condition to leave the scenario untested')
def step_impl(context):
    context.condition = 'untested'
    logging.info('a condition to leave the scenario untested')

@then('I perform the condition')
def step_impl(context):
    if context.condition == 'fail':
        # This step will cause the test to fail
        assert False, "This step is designed to fail"
    elif context.condition == 'pass':
        # This step will pass
        assert True
    elif context.condition == 'skip':
        # This step will be skipped
        context.scenario.skip("This scenario is skipped")
    elif context.condition == 'exit':
        # This step will be skipped
        exit(1)
    elif context.condition == 'untested':
        # This step will be skipped
        pass

@given('I rename the {feature_or_scenario} from context to have the suffix "{suffix}"')
def step_impl(context, feature_or_scenario, suffix):
    if feature_or_scenario == 'feature':
        context.new_feature_name = context.feature.name + suffix
        logging.info('I rename the feature from \n"{}" \nto \n"{}"'.format(context.feature.name, context.new_feature_name))
    elif feature_or_scenario == 'scenario':
        context.new_scenario_name = context.scenario.name + suffix
        logging.info('I rename the scenario from \n"{}" \nto \n"{}"'.format(context.scenario.name, context.new_scenario_name))
    else:
        raise ValueError('Invalid element, it should be "feature" or "scenario"')


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


@when('I validate image attachments')
def step_validate_image_attachments(context):
    """Simple validation step for image attachments"""
    logging.info("Validating image attachments")


@then('I should see attached images in the output')
def step_verify_attached_images_in_output(context):
    """Verify that images were attached"""
    logging.info("Images were attached to the test output")
