def before_all_workers(context):
    # Intentionally setting a non-serializable value to trigger the clear error
    context.bad_value = lambda: None
