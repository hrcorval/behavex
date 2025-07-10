import logging

from behave import given, then


@given('image attachment functionality is required')
def step_require_image_attachment(context):
    """Mark image attachment functionality as required for this scenario."""
    context.require_image_attachments = True


@then('image attachment dependencies should be available')
def step_validate_image_dependencies(context):
    """Validate that image attachment dependencies are available when required."""
    if hasattr(context, 'require_image_attachments') and context.require_image_attachments:
        try:
            from behavex_images import image_attachments
            logging.info("Image attachment dependencies are available")
        except (ImportError, ModuleNotFoundError) as e:
            raise AssertionError(f"Required dependency 'behavex-images' is not available: {e}")
    else:
        logging.info("Image attachment dependencies not required for this test")
