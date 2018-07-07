from .dataObject import DataObject, ObjectProperty, DatatypeProperty


class Module(DataObject):
    '''
    Represents a module of code

    Most modern programming languages organize code into importable modules of one kind or another. This is basically
    the nearest level above a *class* in the language.
    '''


class ModuleAccess(DataObject):
    '''
    Describes how to access a module.

    Module access is how a person or automated system brings the module to where it can be imported/included, possibly
    in a subsequent
    '''


class ClassDescription(DataObject):
    '''
    Describes a class in the programming language
    '''

    module = ObjectProperty(value_type=Module)
    ''' The module the class belongs to '''


class RegistryEntry(DataObject):

    '''
    A mapping from a class in the programming language to an RDF class.

    Objects of this type are utilized in the resolution of classes from the RDF graph
    '''

    class_description = ObjectProperty(value_type=ClassDescription)
    ''' The description of the class '''

    rdf_class = DatatypeProperty()
    ''' The RDF type for the class '''


__yarom_mapped_classes__ = (RegistryEntry, ModuleAccess, ClassDescription, Module)
