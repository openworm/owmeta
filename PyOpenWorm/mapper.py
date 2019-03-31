from __future__ import print_function
import importlib as IM
import logging
import rdflib as R
import yarom
from .configure import Configureable
from .module_recorder import ModuleRecordListener
from itertools import count
from six import with_metaclass
from yarom.mapperUtils import parents_str
from yarom.utils import FCN


__all__ = ["Mapper",
           "UnmappedClassException"]

L = logging.getLogger(__name__)


class UnmappedClassException(Exception):
    pass


class ClassRedefinitionAttempt(Exception):
    pass


class Mapper(ModuleRecordListener, Configureable):
    '''
    Keeps track of relationships between classes, between modules, and between classes and modules
    '''
    _instances = dict()

    @classmethod
    def get_instance(cls, *args):
        if args not in cls._instances:
            cls._instances[args] = Mapper(*args)

        return cls._instances[args]

    def __init__(self, base_class_names, base_namespace=None, imported=(), name=None, **kwargs):
        super(Mapper, self).__init__(**kwargs)

        """ Maps class names to classes """
        self.MappedClasses = dict()

        """ Maps classes to decorated versions of the class """
        self.DecoratedMappedClasses = dict()

        """ Maps RDF types to properties of the related class """
        self.RDFTypeTable = dict()

        if not isinstance(base_class_names, (tuple, list)):
            raise Exception('base_class_names argument must be either a tuple'
                            ' or list')
        """ Names for the base classes """
        self.base_class_names = tuple(base_class_names)
        self.base_modules = set(n.rsplit('.', 1)[0] for n in base_class_names)

        """ The base class for objects that will be mapped.

        Defined once the module containing the class is loaded
        """
        self.base_classes = dict()

        if base_namespace is None:
            base_namespace = R.Namespace("http://example.com#")
        elif not isinstance(base_namespace, R.Namespace):
            base_namespace = R.Namespace(base_namespace)

        """ Base namespace used if a mapped class doesn't define its own """
        self.base_namespace = base_namespace

        """ Modules that have already been loaded """
        self.modules = dict()

        self.imported_mappers = imported

        if name is None:
            name = hex(id(self))
        self.name = name

    def decorate_class(self, cls):
        '''
        Extension point for subclasses of Mapper to apply an operation to all mapped classes
        '''
        return cls

    def add_class(self, cls):
        cname = FCN(cls)
        maybe_cls = self._lookup_class(cname)
        if maybe_cls is not None:
            if maybe_cls is cls:
                return False
            else:
                raise ClassRedefinitionAttempt(maybe_cls, cls)
        L.debug("Adding class %s@0x%x", cls, id(cls))

        self.MappedClasses[cname] = cls
        self.DecoratedMappedClasses[cls] = self.decorate_class(cls)
        parents = cls.__bases__
        L.debug('parents %s', parents_str(cls))

        if hasattr(cls, 'on_mapper_add_class'):
            cls.on_mapper_add_class(self)

        # This part happens after the on_mapper_add_class has run since the
        # class has an opportunity to set its RDF type based on what we provide
        # in the Mapper.
        self.RDFTypeTable[cls.rdf_type] = cls
        return True

    def unmap_all(self):
        for cls in self.MappedClasses:
            cls.unmap()

    def load_module(self, module_name):
        """ Loads the module. """
        module = self.lookup_module(module_name)
        if not module:
            module = IM.import_module(module_name)
            return self.process_module(module_name, module)
        else:
            return module

    def process_module(self, module_name, module):
        self.modules[module_name] = module
        for c in self._module_load_helper(module):
            if hasattr(c, 'after_mapper_module_load'):
                c.after_mapper_module_load(self)
        return module

    def process_class(self, *classes):
        for c in classes:
            self.add_class(c)
            if hasattr(c, 'after_mapper_module_load'):
                c.after_mapper_module_load(self)

    process_classes = process_class

    def lookup_module(self, module_name):
        m = self.modules.get(module_name, None)
        if m is None:
            for p in self.imported_mappers:
                m = p.lookup_module(module_name)
                if m:
                    break
        return m

    def load_class(self, cname_or_mname, cnames=None):
        if cnames:
            mpart = cname_or_mname
        else:
            mpart, cpart = cname_or_mname.rsplit('.', 1)
            cnames = (cpart,)
        m = self.load_module(mpart)
        try:
            res = tuple(self.DecoratedMappedClasses[c]
                        if c in self.DecoratedMappedClasses
                        else c
                        for c in
                        (getattr(m, cname) for cname in cnames))

            return res[0] if len(res) == 1 else res
        except AttributeError:
            raise UnmappedClassException(cnames)

    def _module_load_helper(self, module):
        # TODO: Make this class selector pluggable
        return self.handle_mapped_classes(getattr(module, '__yarom_mapped_classes__', ()))

    def handle_mapped_classes(self, classes):
        res = []
        for cls in classes:
            # This previously used the
            full_class_name = FCN(cls)
            if full_class_name in self.base_class_names:
                L.debug('Setting base class %s', full_class_name)
                self.base_classes[full_class_name] = cls
            if isinstance(cls, type) and self.add_class(cls):
                res.append(cls)

        return sorted(res, key=_ClassOrderable, reverse=True)

    def lookup_class(self, cname):
        """ Gets the class corresponding to a fully-qualified class name """
        ret = self._lookup_class(cname)
        if ret is None:
            raise UnmappedClassException((cname,))
        return ret

    def _lookup_class(self, cname):
        c = self.MappedClasses.get(cname, None)
        if c is None:
            for p in self.imported_mappers:
                c = p._lookup_class(cname)
                if c:
                    break
        else:
            L.debug('%s.lookup_class("%s") %s@%s',
                    repr(self), cname, c, hex(id(c)))
        return c

    def mapped_classes(self):
        for p in self.imported_mappers:
            for c in p.mapped_classes():
                yield
        for c in self.MappedClasses.values():
            yield c

    def __str__(self):
        if self.name is not None:
            return 'Mapper(name="'+str(self.name)+'")'
        else:
            return super(Mapper, self).__str__()


class _ClassOrderable(object):
    def __init__(self, cls):
        self.cls = cls

    def __eq__(self, other):
        self.cls is other.cls

    def __gt__(self, other):
        res = False
        ocls = other.cls
        scls = self.cls
        if issubclass(ocls, scls) and not issubclass(scls, ocls):
            res = True
        elif issubclass(scls, ocls) == issubclass(ocls, scls):
            res = scls.__name__ > ocls.__name__
        return res

    def __lt__(self, other):
        res = False
        ocls = other.cls
        scls = self.cls
        if issubclass(scls, ocls) and not issubclass(ocls, scls):
            res = True
        elif issubclass(scls, ocls) == issubclass(ocls, scls):
            res = scls.__name__ < ocls.__name__
        return res
