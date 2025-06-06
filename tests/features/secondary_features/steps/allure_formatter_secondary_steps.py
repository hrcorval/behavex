import logging

from behave import given, then, when


# Allure-specific test steps for testing formatter functionality
@when('I process the following table')
def step_process_table(context):
    # Process the table data from the step
    if context.table:
        logging.info(f"Processing table with {len(context.table.rows)} rows")
        for row in context.table:
            logging.info(f"Row data: {row.as_dict()}")
    else:
        logging.warning("No table data found in step")


@when('I process the following text')
def step_process_text(context):
    # Process the multiline text from the step
    if context.text:
        logging.info(f"Processing multiline text with {len(context.text.splitlines())} lines")
        logging.info(f"Text content: {context.text}")
    else:
        logging.warning("No multiline text found in step")


@given('a test condition with allure tags')
def step_test_condition_allure_tags(context):
    logging.info("Setting up test condition with allure tags")


@when('I execute an action with epic and story tags')
def step_execute_action_epic_story(context):
    logging.info("Executing action with epic and story tags")


@then('I should see the result processed correctly')
def step_see_result_processed_correctly(context):
    logging.info("Verifying result processing")


@given('another test condition with different tags')
def step_another_test_condition_different_tags(context):
    logging.info("Setting up another test condition with different tags")


@when('I execute another action')
def step_execute_another_action(context):
    logging.info("Executing another action")


@then('I should see different tag processing')
def step_see_different_tag_processing(context):
    logging.info("Verifying different tag processing")


@given('a critical test condition')
def step_critical_test_condition(context):
    logging.info("Setting up critical test condition")


@when('I execute a critical action')
def step_execute_critical_action(context):
    logging.info("Executing critical action")


@then('I should see critical processing')
def step_see_critical_processing(context):
    logging.info("Verifying critical processing")


@given('a test condition with table data')
def step_test_condition_table_data(context):
    logging.info("Setting up test condition with table data")


@then('I should see the table processed correctly')
def step_see_table_processed_correctly(context):
    logging.info("Verifying table processing")


@given('a test condition with multiline text')
def step_test_condition_multiline_text(context):
    logging.info("Setting up test condition with multiline text")


@then('I should see the text processed correctly')
def step_see_text_processed_correctly(context):
    logging.info("Verifying text processing")
