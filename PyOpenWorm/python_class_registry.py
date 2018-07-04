from .dataObject import DatatypeProperty
from .class_registry import Module, ModuleAccess


class PythonModule(Module):
    '''
    A Python module
    '''


class PyPIPackage(ModuleAccess):

    '''
    Describes a package hosted on the Python Package Index (PyPI)
    '''

    package_name = DatatypeProperty()
    package_version = DatatypeProperty()
