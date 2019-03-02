from pprint import pprint
import importlib as IM
import logging
from types import ModuleType
L = logging.getLogger(__name__)


class ModuleRecorder(object):
    def __init__(self, **kwargs):

        # Module relationship
        self.ModuleDependencies = dict()
        self.ModuleDependents = dict()
        self._listeners = []
        self.mapdepth = 0
        self.loading_module = None
        self._module_insertion_order = dict()
        self._modcnt = 0

    def add_listener(self, listener, replay=True):
        if replay:
            self._replay_modules(listener)
        self._listeners.append(listener)

    def remove_listener(self, listener):
        if listener in self._listeners:
            self._listeners.remove(listener)

    def _replay_modules(self, listener):
        for name, module in self._module_record:
            listener.process_module(name, module)

    @property
    def _module_record(self):
        for name, value in sorted(self._module_insertion_order.items(), key=lambda item: item[1][0]):
            yield name, value[1]

    def process_module(self, module=None, cb=None, module_name=None, caller=None):
        if module is None:
            if cb is None:
                raise ValueError("At least one of cb or module argument must"
                                 " be provided")
            if module_name is None:
                raise ValueError("At least one of module argument or"
                                 " module_name must be provided")
        if module_name is None:
            module_name = module.__name__

        L.debug("%sLOADING %s", ' ' * self.mapdepth, module_name)
        self.mapdepth += 1
        try:
            if caller is None:
                previously_loading = self.loading_module
            else:
                previously_loading = caller

            self.loading_module = module_name

            if cb is not None:
                x = cb()
                if module is None:
                    module = x

            proper_module_name = module.__name__
            actual_module = module

            # We may get a top-level package rather than the module we asked for -- we detect this checking the prefix
            # of the retrieved package/module name
            if module_name.startswith(module.__name__ + '.'):
                remaining_attrs = module_name.split('.')[1:]
                current_position = module
                match = True
                for attr in remaining_attrs:
                    maybe_module = getattr(module, attr, None)
                    if not isinstance(maybe_module, ModuleType):
                        match = False
                        break
                    else:
                        current_position = maybe_module
                if match and current_position.__name__ == module_name:
                    proper_module_name = module_name
                    actual_module = current_position

            self.add_module_record(actual_module)
            self.update_module_dependencies(proper_module_name, actual_module.__name__)
            self.add_module_dependency(previously_loading, proper_module_name)

            for listener in self._listeners:
                listener.process_module(proper_module_name, actual_module)
        finally:
            self.loading_module = previously_loading
            self.mapdepth -= 1
        return module

    def add_module_record(self, module):
        if module.__name__ not in self._module_insertion_order:
            self._module_insertion_order[module.__name__] = (self._modcnt, module)
            self._modcnt += 1

    def add_module_dependency(self, loading_module, module_name):
        if module_name == loading_module or module_name.startswith(loading_module + '.'):
            return

        if loading_module:
            depends = self.ModuleDependencies.get(loading_module, set())
            depends.add(module_name)
            self.ModuleDependencies[loading_module] = depends

            callers = self.ModuleDependents.get(module_name, set())
            callers.add(loading_module)
            self.ModuleDependents[module_name] = callers
        else:
            self.ModuleDependents[module_name] = set()

    def update_module_dependencies(self, old_name, new_name):
        if new_name != old_name:
            if old_name in self.ModuleDependencies:
                self.ModuleDependencies[new_name] = self.ModuleDependencies[old_name]
                del self.ModuleDependencies[old_name]

            for dependents in self.ModuleDependents.values():
                if old_name in dependents:
                    dependents.add(new_name)
                    dependents.remove(old_name)


class ModuleRecordListener(object):
    def process_module(self, module_name, module):
        raise NotImplementedError()
