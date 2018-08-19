from .cli_common import METHOD_NAMED_ARG

CLI_HINTS = {
    'PyOpenWorm.command.POW': {
        'commit': {
            (METHOD_NAMED_ARG, 'message'): {
                'names': ['--message', '-m'],
            },
        },
        'clone': {
            (METHOD_NAMED_ARG, 'url'): {
                'names': ['url'],
            },
        },
        'translate': {
            (METHOD_NAMED_ARG, 'translator'): {
                'names': ['translator']
            },
            (METHOD_NAMED_ARG, 'data_sources'): {
                'nargs': '*',
                'names': ['data_sources'],
            },
        },
        'serialize': {
            (METHOD_NAMED_ARG, 'destination'): {
                'names': ['--destination', '-w']
            },
            (METHOD_NAMED_ARG, 'format'): {
                'names': ['--format', '-f']
            },
        },
        'IGNORE': ['message', 'progress_reporter']
    },
    'PyOpenWorm.command.POWSource': {
        'show': {
            (METHOD_NAMED_ARG, 'data_source'): {
                'names': ['data_source'],
            },
        },
    },
    'PyOpenWorm.command.POWTranslator': {
        'show': {
            (METHOD_NAMED_ARG, 'translator'): {
                'names': ['translator'],
            },
        },
    },
}
