import rdflib as R
from PyOpenWorm import DataUser
import PyOpenWorm as P
import traceback

__all__ = [ "DataObjectMapper"]

_DataObjects = dict()
# TODO: Put the subclass relationships in the database
_DataObjectsParents = dict()

def makeDatatypeProperty(*args,**kwargs):
    """ Create a SimpleProperty that has a simple type (string,number,etc) as its value

    Parameters
    ----------
    linkName : string
        The name of this Property.
    """
    return _create_property(*args,property_type='DatatypeProperty',**kwargs)

def makeObjectProperty(*args,**kwargs):
    """ Create a SimpleProperty that has a complex DataObject as its value

    Parameters
    ----------
    linkName : string
        The name of this Property.
    value_type : type
        The type of DataObject fro values of this property
    """
    return _create_property(*args,property_type='ObjectProperty',**kwargs)

def _create_property(owner_class, linkName, property_type, value_type=False):
    #XXX This should actually get called for all of the properties when their owner
    #    classes are defined.
    #    The initialization, however, must happen with the owner object's creation
    owner_class_name = owner_class.__name__
    property_class_name = owner_class_name + "_" + linkName
    if value_type == False:
        value_type = P.DataObject

    c = None
    if property_class_name in _DataObjects:
        c = _DataObjects[property_class_name]
    else:
        x = None
        if property_type == 'ObjectProperty':
            value_rdf_type = value_type.rdf_type
            x = P.ObjectProperty
        else:
            value_rdf_type = False
            x = P.DatatypeProperty

        c = type(property_class_name,(x,),dict(linkName=linkName, property_type=property_type, value_rdf_type=value_rdf_type, owner_type=owner_class))

    owner_class.dataObjectProperties.append(c)

    return c

class DataObjectMapper(type):
    def __init__(cls, name, bases, dct, conf=False):
        bs = list(bases)
        cls.du = DataUser()
        type.__init__(cls,name,tuple(bs),dct)
        cls.dataObjectProperties = []
        #print 'doing init for', cls
        for x in bs:
            try:
                cls.dataObjectProperties += x.dataObjectProperties
            except AttributeError:
                pass
        cls.register()

    @classmethod
    def setUpDB(self):
        pass

    @classmethod
    def makeClass(cls, name, bases, objectProperties=False, datatypeProperties=False):
        # Need to distinguish datatype and object properties...
        if not datatypeProperties:
            datatypeProperties = []
        if not objectProperties:
            objectProperties = []
        DataObjectMapper(name, bases, dict(objectProperties=objectProperties, datatypeProperties=datatypeProperties))

    def register(cls):
        _DataObjects[cls.__name__] = cls
        _DataObjectsParents[cls.__name__] = [x for x in cls.__bases__ if isinstance(x, DataObjectMapper)]

        cls.parents = _DataObjectsParents[cls.__name__]
        cls.rdf_type = cls.conf['rdf.namespace'][cls.__name__]
        cls.rdf_namespace = R.Namespace(cls.rdf_type + "/")

        cls.addParentsToGraph()

        cls.addObjectProperties()
        cls.addDatatypeProperties()

        cls.addPropertiesToGraph()
        cls.addNamespaceToManager()

        setattr(P, cls.__name__, cls)

    def addNamespaceToManager(cls):
        cls.conf['rdf.namespace_manager'].bind(cls.__name__, cls.rdf_namespace)

    def addPropertiesToGraph(cls):
        deets = []
        for x in cls.dataObjectProperties:
            deets.append((x.rdf_type, cls.conf['rdf.namespace']['domain'], cls.rdf_type))
        cls.du.add_statements(deets)

    def addParentsToGraph(cls):
        deets = []
        for y in cls.parents:
            deets.append((cls.rdf_type, R.RDFS['subClassOf'], y.rdf_type))
        cls.du.add_statements(deets)

    def addObjectProperties(cls):
        try:
            for x in cls.objectProperties:
                if isinstance(x,tuple):
                    makeObjectProperty(cls,x[0], value_type=x[1])
                else:
                    makeObjectProperty(cls,x)
        except AttributeError:
            pass
        except:
            traceback.print_exc()

    def addDatatypeProperties(cls):
        # Also get all of the properites
        try:
            for x in cls.datatypeProperties:
                makeDatatypeProperty(cls,x)
        except AttributeError:
            pass
        except:
            traceback.print_exc()

    def oid(self,identifier,rdf_type=False):
        """ Load an object from the database using its type tag """
        # XXX: This is a class method because we need to get the conf
        # We should be able to extract the type from the identifier
        if rdf_type:
            uri = rdf_type
        else:
            uri = identifier

        cn = self._extract_class_name(uri)
        # if its our class name, then make our own object
        # if there's a part after that, that's the property name
        o = _DataObjects[cn](ident=identifier)
        return o

