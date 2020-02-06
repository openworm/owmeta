from owmeta_core.cli_common import METHOD_NAMED_ARG

CLI_HINTS = {
    'owmeta.command.OWMEvidence': {
        'get': {
            (METHOD_NAMED_ARG, 'identifier'): {
                'names': ['identifier'],
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
