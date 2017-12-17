import builtins
import wrapt
from PyOpenWorm.import_contextualizer import ImportContextualizer


class Overrider(object):
    def __init__(self, mapper):
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

    def wrap_import(self):
        wrapped = builtins.__import__
        builtins.__import__ = self.import_wrapper(wrapped)
