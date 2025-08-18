
def before_all(context):
    # Configure behavex-images to always attach images to reports
    try:
        from behavex_images import image_attachments
        from behavex_images.image_attachments import AttachmentsCondition
        image_attachments.set_attachments_condition(context, AttachmentsCondition.ALWAYS)
    except (ImportError, ModuleNotFoundError):
        pass  # behavex-images not available


def before_scenario(context, scenario):
    context.progress_bar = False


def after_feature(context, feature):
    """Ensure after_feature hook is called by behave (required for behave 1.2.7+ compatibility)"""
    # Call BehavEx after_feature directly since hook interception doesn't receive the feature object
    try:
        from behavex import environment as behavex_env
        behavex_env.after_feature(context, feature)
    except Exception:
        pass  # Ignore errors to avoid breaking test execution


def after_scenario(context, scenario):
    """Ensure after_scenario hook is called by behave (required for behave 1.2.7+ compatibility)"""
    # Call BehavEx after_scenario directly to ensure it's always called
    try:
        from behavex import environment as behavex_env
        behavex_env.after_scenario(context, scenario)
    except Exception:
        pass  # Ignore errors to avoid breaking test execution
