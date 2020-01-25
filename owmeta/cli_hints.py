from .cli_common import METHOD_NAMED_ARG

CLI_HINTS = {
    'owmeta.command.OWM': {
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
    'owmeta.command.OWMContexts': {
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
    'owmeta.commands.bundle.OWMBundleRemote': {
        'add': {
            (METHOD_NAMED_ARG, 'name'): {
                'names': ['name'],
            },
            (METHOD_NAMED_ARG, 'url'): {
                'names': ['url'],
            },
        },
    },
    'owmeta.commands.bundle.OWMBundle': {
        'fetch': {
            (METHOD_NAMED_ARG, 'bundle_id'): {
                'names': ['bundle_id'],
            },
        },
        'load': {
            (METHOD_NAMED_ARG, 'input_file_name'): {
                'names': ['input'],
            },
        },
        'save': {
            (METHOD_NAMED_ARG, 'output'): {
                'names': ['output'],
            },
        },
        'install': {
            (METHOD_NAMED_ARG, 'bundle'): {
                'names': ['bundle'],
            },
        },
        'deregister': {
            (METHOD_NAMED_ARG, 'bundle_id'): {
                'names': ['bundle_id'],
            },
        },
        'register': {
            (METHOD_NAMED_ARG, 'descriptor'): {
                'names': ['descriptor'],
            },
        },
        'deploy': {
            (METHOD_NAMED_ARG, 'bundle_id'): {
                'names': ['bundle_id'],
            },
        },
        'checkout': {
            (METHOD_NAMED_ARG, 'bundle_id'): {
                'names': ['bundle_id'],
            },
        },
    },
    'owmeta.command.OWMSource': {
        'show': {
            (METHOD_NAMED_ARG, 'data_source'): {
                'names': ['data_source'],
            },
        },
        'derivs': {
            (METHOD_NAMED_ARG, 'data_source'): {
                'names': ['data_source'],
            },
        },
    },
    'owmeta.command.OWMSourceData': {
        'retrieve': {
            (METHOD_NAMED_ARG, 'source'): {
                'names': ['source'],
            },
            (METHOD_NAMED_ARG, 'archive'): {
                'names': ['archive'],
            },
        },
    },
    'owmeta.command.OWMTranslator': {
        'show': {
            (METHOD_NAMED_ARG, 'translator'): {
                'names': ['translator'],
            },
        },
    },
    'owmeta.command.OWMEvidence': {
        'get': {
            (METHOD_NAMED_ARG, 'identifier'): {
                'names': ['identifier'],
            },
        },
    },
    'owmeta.command.OWMConfig': {
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
    'owmeta.commands.biology.CellCmd': {
        'show': {
            (METHOD_NAMED_ARG, 'cell_name_or_id'): {
                'names': ['cell_name_or_id'],
            },
        },
    },
}
