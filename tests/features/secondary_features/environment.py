
def before_all(context):
    # Configure behavex-images to always attach images to reports
    try:
        from behavex_images import image_attachments
        from behavex_images.image_attachments import AttachmentsCondition
        image_attachments.set_attachments_condition(context, AttachmentsCondition.ALWAYS)
    except (ImportError, ModuleNotFoundError):
        pass  # behavex-images not available


def after_scenario(context, scenario):
    if hasattr(context, 'new_scenario_name'):
        scenario.name = context.new_scenario_name
    if hasattr(context, 'new_feature_name'):
        scenario.feature.name = context.new_feature_name
