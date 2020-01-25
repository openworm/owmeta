import six

from ..command_util import GeneratorWithData
from ..cell import Cell


class CellCmd(object):
    '''
    Commands for dealing with biological cells
    '''

    def __init__(self, parent, *args, **kwargs):
        self._parent = parent

    def show(self, cell_name_or_id, context=None):
        '''
        Show information about the cell

        Parameters
        ----------
        cell_name_or_id : str
            Cell name or Cell URI
        context : str
            Context to search in. Optional, defaults to the default context.
        '''

        if not context:
            ctx = self._parent._default_ctx
        else:
            ctx = Context(context)

        def helper():
            for cell in ctx.stored(Cell).query(name=cell_name_or_id).load():
                yield cell
                break
            else: # no break
                uri = self._parent._den3(cell_name_or_id)
                for x in ctx.stored(Cell)(ident=uri).load():
                    yield cell

        def fmt_text(cell):
            try:
                sio = six.StringIO()

                nm = self._parent._conf('rdf.namespace_manager')
                print('%s(%s)' % (cell.__class__.__name__, nm.normalizeUri(cell.identifier)), file=sio)
                print('    Lineage name: %s' % cell.lineageName(), file=sio)
                print('    Name: %s' % cell.name(), file=sio)
                print('    WormBase ID: %s' % cell.wormbaseID(), end='', file=sio)
                return sio.getvalue()
            except AttributeError:
                res = str(cell)
                L.error('Failed while creating formatting string representation for %s', res)
                return res

        return GeneratorWithData(helper(), text_format=fmt_text)
