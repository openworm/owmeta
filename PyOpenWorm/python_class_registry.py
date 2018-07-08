from .dataObject import DatatypeProperty
from .class_registry import Module, ModuleAccess, ClassDescription


class PythonModule(Module):
    '''
    A Python module
    '''

    name = DatatypeProperty(multiple=False)
    ''' The full name of the module '''

    def defined_augment(self):
        return self.name.has_defined_value()

    def identifier_augment(self):
        return self.make_identifier_direct(str(self.name.defined_values[0].identifier))


class PyPIPackage(ModuleAccess):

    '''
    Describes a package hosted on the Python Package Index (PyPI)
    '''

    name = DatatypeProperty()
    version = DatatypeProperty()


class PythonClassDescription(ClassDescription):
    name = DatatypeProperty()
    ''' Local name of the class (i.e., relative to the module name) '''

    def defined_augment(self):
        return self.name.has_defined_value() and self.module.has_defined_value()

    def identifier_augment(self):
        return self.make_identifier(self.name.defined_values[0].identifier.n3() +
                                    self.module.defined_values[0].identifier.n3())


__yarom_mapped_classes__ = (PythonModule, PyPIPackage, PythonClassDescription)
