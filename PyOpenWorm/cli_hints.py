from .cli_common import METHOD_NAMED_ARG

CLI_HINTS = {
    'PyOpenWorm.command.POW': {
        'commit': {
            (METHOD_NAMED_ARG, 'message'): {
                'names': ['--message', '-m'],
            },
        },
        'context': {
            (METHOD_NAMED_ARG, 'context'): {
                'nargs': '?',
                'names': ['context'],
            },
        },
        'imports_context': {
            (METHOD_NAMED_ARG, 'context'): {
                'nargs': '?',
                'names': ['context'],
            },
        },
        'clone': {
            (METHOD_NAMED_ARG, 'url'): {
                'names': ['url'],
            },
        },
        'translate': {
            (METHOD_NAMED_ARG, 'output_key'): {
                'names': ['--output-key']
            },
            (METHOD_NAMED_ARG, 'output_identifier'): {
                'names': ['--output-identifier']
            },
            (METHOD_NAMED_ARG, 'translator'): {
                'names': ['translator']
            },
            (METHOD_NAMED_ARG, 'data_sources'): {
                'nargs': '*',
                'names': ['data_sources'],
            },
        },
        'say': {
            (METHOD_NAMED_ARG, 'subject'): {
                'names': ['subject']
            },
            (METHOD_NAMED_ARG, 'property'): {
                'names': ['property']
            },
            (METHOD_NAMED_ARG, 'object'): {
                'names': ['object']
            }
        },
        'save': {
            (METHOD_NAMED_ARG, 'module'): {
                'names': ['module']
            }
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
    'PyOpenWorm.command.POWContexts': {
        'edit': {
            (METHOD_NAMED_ARG, 'context'): {
                'names': ['context'],
                'nargs': '?'
            },
            (METHOD_NAMED_ARG, 'list_formats'): {
                'names': ['--list-formats'],
                'nargs': '?'
            }
        }
    },
    'PyOpenWorm.command.POWSource': {
        'show': {
            (METHOD_NAMED_ARG, 'data_source'): {
                'names': ['data_source'],
            },
        },
    },
    'PyOpenWorm.command.POWSourceData': {
        'retrieve': {
            (METHOD_NAMED_ARG, 'source'): {
                'names': ['source'],
            },
            (METHOD_NAMED_ARG, 'archive'): {
                'names': ['archive'],
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
    'PyOpenWorm.command.POWEvidence': {
        'get': {
            (METHOD_NAMED_ARG, 'identifier'): {
                'names': ['identifier'],
            },
        },
    },
    'PyOpenWorm.command.POWConfig': {
        'set': {
            (METHOD_NAMED_ARG, 'key'): {
                'names': ['key'],
            },
            (METHOD_NAMED_ARG, 'value'): {
                'names': ['value'],
            },
        },
        'get': {
            (METHOD_NAMED_ARG, 'key'): {
                'names': ['key'],
            },
        },
        'delete': {
            (METHOD_NAMED_ARG, 'key'): {
                'names': ['key'],
            },
        },
    },
}
