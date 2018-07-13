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
        'serialize': {
            (METHOD_NAMED_ARG, 'destination'): {
                'names': ['--destination', '-w']
            },
            (METHOD_NAMED_ARG, 'format'): {
                'names': ['--format', '-f']
            },
        },
    },
}
