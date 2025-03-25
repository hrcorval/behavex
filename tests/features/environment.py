
def before_scenario(context, scenario):
    context.progress_bar = False

def before_step(context, step):
    context.step = step
