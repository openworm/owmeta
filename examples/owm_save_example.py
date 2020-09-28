from owmeta_core.dataobject import DataObject
from owmeta_core.context import Context


def owm_data(namespace):
    # Make a new context. Takes care of specifying the `conf` argument and enables
    # validation for statements
    ctx = namespace.new_context("http://example.org/example_context")

    ctx(DataObject)(key='a')
    ctx(DataObject)(key='b')

    # Add an import of DataObject's context, but see openworm/owmeta#374 -- may be
    # automated eventually
    ctx.add_import(DataObject.definition_context)

    # Link to the namespace context -- our statements will not be saved otherwise
    namespace.context.add_import(ctx)
