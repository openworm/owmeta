import wrapt
from PyOpenWorm.import_contextualizer import ImportContextualizer
import six


class Overrider(object):
    instances = dict()

    def __new__(cls, mapper):
        if len(Overrider.instances.keys()) > 1:
            raise Exception('Only one Overrider should exist. There are overriders for these: ' +
                            ' '.join(str(x) for x in Overrider.instances.keys()))

        inst = Overrider.instances.get(mapper, None)
        if inst is not None:
            return inst
        sup = super(Overrider, cls).__new__(cls)
        Overrider.instances[mapper] = sup
        return sup

    def __init__(self, mapper):
        if hasattr(self, 'mapper') and self.mapper is not None:
            return

        self.i = 0
        self.k = 0
        self.mapper = mapper

        @wrapt.function_wrapper
        def import_wrapper(orig__import__, __, args, kwargs):
            self.k += 1
            self.i += 1
            try:
                m = [None, None]
                if len(args) > 4 and args[4]:
                    depth = args[4]

                    if args[1] is None:
                        raise ImportError("No globals given to import to detect calling module for relative import")

                    caller = args[1].get('__name__', None)

                    if caller is None:
                        raise ImportError("No calling module in import globals to resolve relative import")

                    parent = caller.rsplit('.', depth)[0]
                    module_name = parent + '.' + args[0]
                else:
                    module_name = args[0]

                def cb():
                    if len(args) >= 3:
                        importer_locals = args[2]
                        if importer_locals is not None:
                            splits = module_name.split('.', 1)
                            if len(splits) == 2:
                                first, rest = splits
                                local = importer_locals.get(first, None)
                                if isinstance(local, ImportContextualizer):
                                    new_args = list(args)
                                    new_args[0] = rest
                                    m[0] = local
                                    if len(new_args) >= 4:
                                        m[1] = new_args[3]
                                    return orig__import__(*new_args, **kwargs)
                    return orig__import__(*args, **kwargs)

                def cb1():
                    return orig__import__(*args, **kwargs)

                def mb(mod):
                    if m[0] is not None:
                        return m[0](mod)
                    else:
                        return mod

                return mb(self.mapper.process_module(module_name=module_name, cb=cb))
            finally:
                self.i -= 1
        self.import_wrapper = import_wrapper
        self.wrapped = None

    def install_excepthook(self):
        import traceback
        import sys

        def filtering_except_hook(type, value, tb):
            s = ['Traceback (most recent call last, import_override removed):\n']
            s += traceback.format_list([x for x in traceback.extract_tb(tb)
                                        if x[2] != 'process_module' and
                                        not x[0].endswith('PyOpenWorm/import_override.py') and
                                        not (x[0].endswith('wrapt/wrappers.py') and x[2] == '__call__')])
            s += traceback.format_exception_only(type, value)
            for l in s:
                six.print_(l, file=sys.stderr, end='')
        sys.excepthook = filtering_except_hook

    def wrap_import(self):
        builtins = six.moves.builtins
        if self.wrapped is None:
            if not hasattr(builtins, '__import__'):
                raise Exception("'builtins' module does not have an '__import__' attribute."
                                " Cannot override import mechanism")
            self.wrapped = builtins.__import__

        builtins.__import__ = self.import_wrapper(self.wrapped)
