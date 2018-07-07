from .dataObject import DatatypeProperty
from .class_registry import Module, ModuleAccess, ClassDescription


class PythonModule(Module):
    '''
    A Python module
    '''

    name = DatatypeProperty(multiple=False)
    ''' The full name of the module '''


class PyPIPackage(ModuleAccess):

    '''
    Describes a package hosted on the Python Package Index (PyPI)
    '''

    name = DatatypeProperty()
    version = DatatypeProperty()


class PythonClassDescription(ClassDescription):
    name = DatatypeProperty()
    ''' Local name of the class (i.e., relative to the module name) '''


__yarom_mapped_classes__ = (PythonModule, PyPIPackage, PythonClassDescription)
