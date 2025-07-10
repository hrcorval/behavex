
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
