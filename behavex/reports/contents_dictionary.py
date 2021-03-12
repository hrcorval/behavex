# -*- encoding: utf-8 -*e
"""
/*
* BehaveX - BDD testing library based on Behave
*/

This module provides a dictionary with the contents that are displayed in
test execution reports.

Variables:
    - TEXTS
"""

TEXTS = {
    'commons': {
        'expand': 'Expand the {} information',
        'collapse': 'Collapse the {} information',
        'error_background': 'Error in background',
        'framework_name': 'BehaveX',
        'framework_description': 'Agile test wrapper on top of Behave (BDD)',
        'help': {
            'title': 'Click here for more details'
        },
        'text': {
            'total_time': 'Total execution time'
        },
        'footer': {
            'name': 'BehaveX'
        }

    },
    'report': {
        'title': 'Test Report',
        'description': '',
        'modal': {
            'title': '',
            'body': '',
        },
        'test_to_fix': 'There are some issues in this scenario that are under '
                       'fix process <small class="text-center">'
                       '(@TEST_TO_FIX tag).</small>',
        'bug_to_fix': 'There is a product bug under fix process that affects '
                      'this scenario <small class="text-center">'
                      '(@BUG_TO_FIX tag).</small>',
        'show_background': '(show background)',
        'hide_background': '(hide background)',
        'execution_tag': 'Execution Tag',
        'filter_tag': {
            'label': 'Tag'
        },
        'reset_filter': {
            'label': 'Reset'
        },
        'skip_fix_process': {
            'label': 'Skip scenarios under fix process'
        },
        'icon_duplicate': {
            'title': 'Copy link to this scenario'
        },
        'icon_repeat': {
            'title': 'This scenario was executed two times'
        },
        'filter_status': {
            'label': 'Status'
        }
    },
    'tags': {
        'title': 'Tags',
        'description': '',
        'modal': {
            'title': '',
            'body': ''
        }
    },
    'steps': {
        'title': 'Steps',
        'description': '',
        'modal': {
            'title': '',
            'body': ''
        }
    },
    'metrics': {
        'title': 'Metrics',
        'description': '',
        'modal': {
            'title': '',
            'body': '<b>Test Automation Rate:</b> % of automated scenarios.<br>'
                    '<b>Pass Rate:</b>: % of passed scenarios.<br>'
        },
        'checkbox': {
            'include_skipped': 'Include not executed tests',
            'include_fix_process': 'Include failed scenarios under fix process'
                                   '<br><small>(tagged as @TEST_TO_FIX or '
                                   '@BUG_TO_FIX)</small></b>'
        }
    },
    'joined': {
        'title': '',
        'description': '',
        'modal': {
            'title': '',
            'modal': 'the'
        }
    },
    'feature': {
        'serial_execution': '{0}\nRunning serial features (tagged as @SERIAL)'
        '.\n\n{0}'.format('*' * 60),
        'running_parallels': '{0}\nRunning parallel features.\n\n{0}'.format('*' * 60),
        'run_behave': u"Running feature '{}'."
    },
    'scenario': {
        'serial_execution':  u'{0}\nRunning serial scenarios (tagged as @SERIAL)'
        u'\n\n{0}'.format('*' * 60),
        'running_parallels':   u'{0}\nRunning parallel scenarios\n\n{0}'.format('*' * 60),
        'run_behave': u"Running feature '{}' with scenario '{}'."
    },
    'folder': {
        'run_behave': u"Running folder: '{}' and feature '{}'."
    },
    'path': {'not_found': u'\nThe path "{}" was not found.\n'}
}
