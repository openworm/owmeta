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

                def cb():
                    if len(args) >= 3:
                        importer_locals = args[2]
                        if importer_locals is not None:
                            module_name = args[0]
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

                def mb(mod):
                    if m[0] is not None:
                        return m[0](mod)
                    else:
                        return mod

                return mb(self.mapper.process_module(module_name=args[0], cb=cb))
            finally:
                self.i -= 1
        self.import_wrapper = import_wrapper
        self.wrapped = None

    def wrap_import(self):
        builtins = six.moves.builtins
        if self.wrapped is None:
            if not hasattr(builtins, '__import__'):
                raise Exception("'builtins' module does not have an '__import__' attribute."
                                " Cannot override import mechanism")
            self.wrapped = builtins.__import__

        builtins.__import__ = self.import_wrapper(self.wrapped)
