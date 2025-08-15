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
def given_failing_condition(context):
    context.condition = 'fail'
    logging.info('a failing condition')

@given('a passing condition')
def given_passing_condition(context):
    context.condition = 'pass'
    logging.info('a passing condition')

@given('image attachments are set to ONLY_ON_FAILURE condition')
def given_image_attachments_only_on_failure(context):
    """Set image attachments to ONLY_ON_FAILURE condition"""
    try:
        from behavex_images import image_attachments
        from behavex_images.image_attachments import AttachmentsCondition
        image_attachments.set_attachments_condition(context, AttachmentsCondition.ONLY_ON_FAILURE)
        logging.info('Image attachments set to ONLY_ON_FAILURE condition')
    except (ImportError, ModuleNotFoundError):
        logging.warning('behavex-images not available, skipping attachment condition setup')

@then('a failing condition is performed')
def then_failing_condition_performed(context):
    """Perform a failing assertion to create failed status"""
    logging.info('Performing failing condition - this will cause failed status')
    assert False, "This step is designed to fail"



@given('a passing condition that records execution order "{order_tag}"')
def given_passing_condition_with_order(context, order_tag):
    context.condition = 'pass'
    # Record execution order for testing purposes
    if not hasattr(context, 'execution_order'):
        context.execution_order = []
    context.execution_order.append(order_tag)
    logging.info(f'a passing condition that records execution order "{order_tag}"')

@given('a condition to skip the scenario')
def given_skip_condition(context):
    context.condition = 'skip'
    logging.info('a condition to skip the scenario')

@given('a condition to exit the scenario')
def given_exit_condition(context):
    context.condition = 'exit'
    logging.info('a condition to exit the scenario')

@given('a condition to leave the scenario untested')
def given_untested_condition(context):
    context.condition = 'untested'
    logging.info('a condition to leave the scenario untested')

@then('I perform the condition')
def then_perform_condition(context):
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
def given_rename_feature_or_scenario(context, feature_or_scenario, suffix):
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


# Simple step definitions for test subject feature files
@given('a simple test condition')
def step_simple_test_condition(context):
    """Simple test condition for test subject scenarios"""
    context.test_condition = True
    logging.info("Simple test condition established")


@when('I perform a simple action')
def step_perform_simple_action(context):
    """Simple action for test subject scenarios"""
    context.action_performed = True
    logging.info("Simple action performed")


@then('I should see a simple result')
def step_simple_result(context):
    """Simple result verification for test subject scenarios"""
    assert context.test_condition, "Test condition was not established"
    assert context.action_performed, "Action was not performed"
    logging.info("Simple result verified")


# Step definitions for allure_text_tests.feature
@given('a test condition with multiline text')
def step_test_condition_with_multiline_text(context):
    """Test condition with multiline text"""
    context.multiline_text_condition = True
    logging.info("Test condition with multiline text established")


@when('I process the following text:')
def step_process_multiline_text(context):
    """Process multiline text"""
    context.processed_text = context.text
    context.text_processing_action = True
    logging.info("Multiline text processed")


@then('I should see the text processed correctly')
def step_see_text_processed_correctly(context):
    """Verify text processed correctly"""
    assert context.multiline_text_condition, "Multiline text condition was not established"
    assert context.text_processing_action, "Text processing action was not executed"
    assert context.processed_text, "Text was not processed"
    logging.info("Text processing verified")


# Step definitions for allure_table_tests.feature
@given('a test condition with table data')
def step_test_condition_with_table_data(context):
    """Test condition with table data"""
    context.table_data_condition = True
    logging.info("Test condition with table data established")


@when('I process the following table:')
def step_process_table_data(context):
    """Process table data"""
    context.processed_table = context.table
    context.table_processing_action = True
    logging.info("Table data processed")


@then('I should see the table processed correctly')
def step_see_table_processed_correctly(context):
    """Verify table processed correctly"""
    assert context.table_data_condition, "Table data condition was not established"
    assert context.table_processing_action, "Table processing action was not executed"
    assert context.processed_table, "Table was not processed"
    logging.info("Table processing verified")


# Step definitions for allure_tagged_tests.feature
@given('a test condition with allure tags')
def step_test_condition_with_allure_tags(context):
    """Test condition with allure tags"""
    context.allure_tags_condition = True
    logging.info("Test condition with allure tags established")


@given('another test condition with different tags')
def step_another_test_condition_with_different_tags(context):
    """Another test condition with different tags"""
    context.different_tags_condition = True
    logging.info("Another test condition with different tags established")


@given('a critical test condition')
def step_critical_test_condition(context):
    """Critical test condition"""
    context.critical_condition = True
    logging.info("Critical test condition established")


@when('I execute an action with epic and story tags')
def step_execute_action_with_epic_story_tags(context):
    """Execute action with epic and story tags"""
    context.epic_story_action = True
    logging.info("Action with epic and story tags executed")


@when('I execute another action')
def step_execute_another_action(context):
    """Execute another action"""
    context.another_action = True
    logging.info("Another action executed")


@when('I execute a critical action')
def step_execute_critical_action(context):
    """Execute a critical action"""
    context.critical_action = True
    logging.info("Critical action executed")


@then('I should see the result processed correctly')
def step_see_result_processed_correctly(context):
    """Verify result processed correctly"""
    assert context.allure_tags_condition, "Allure tags condition was not established"
    assert context.epic_story_action, "Epic story action was not executed"
    logging.info("Result processed correctly")


@then('I should see different tag processing')
def step_see_different_tag_processing(context):
    """Verify different tag processing"""
    assert context.different_tags_condition, "Different tags condition was not established"
    assert context.another_action, "Another action was not executed"
    logging.info("Different tag processing verified")


@then('I should see critical processing')
def step_see_critical_processing(context):
    """Verify critical processing"""
    assert context.critical_condition, "Critical condition was not established"
    assert context.critical_action, "Critical action was not executed"
    logging.info("Critical processing verified")
