import threading


def before_scenario(context, scenario):
    if 'CRASHING_BEFORE_SCENARIO' in scenario.tags:
        threading.interrupt_main()
