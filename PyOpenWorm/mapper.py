import rdflib as R
from PyOpenWorm import DataUser
import PyOpenWorm as P
import traceback

__all__ = [ "DataObjectMapper", "_DataObjectsParents"]

_DataObjects = dict()
# TODO: Put the subclass relationships in the database
_DataObjectsParents = dict()

def DatatypeProperty(*args,**kwargs):
    """ Create a SimpleProperty that has a simple type (string,number,etc) as its value

    Parameters
    ----------
    linkName : string
        The name of this Property.
    """
    return _create_property(*args,property_type='DatatypeProperty',**kwargs)

def ObjectProperty(*args,**kwargs):
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
        if property_type == 'ObjectProperty':
            value_rdf_type = value_type.rdf_type
        else:
            value_rdf_type = False

        c = type(property_class_name,(P.SimpleProperty,),dict(linkName=linkName, property_type=property_type, value_rdf_type=value_rdf_type, owner_type=owner_class))

    owner_class.bones.append(c)

    return c

class DataObjectMapper(type):
    def __init__(cls, name, bases, dct, conf=False):
        bs = list(bases)
        cls.du = DataUser(conf)
        type.__init__(cls,name,tuple(bs),dct)
        cls.bones = []
        #print 'doing init for', cls
        for x in bs:
            try:
                cls.bones += x.bones
            except AttributeError:
                pass
        cls.register()

    @classmethod
    def setUpDB(self):
        pass

    def register(cls):
        _DataObjects[cls.__name__] = cls
        _DataObjectsParents[cls.__name__] = [x for x in cls.__bases__ if isinstance(x, DataObjectMapper)]

        cls.parents = _DataObjectsParents[cls.__name__]
        cls.rdf_type = cls.conf['rdf.namespace'][cls.__name__]
        cls.rdf_namespace = R.Namespace(cls.rdf_type + "/")

        deets = []
        for y in cls.parents:
            deets.append((cls.rdf_type, R.RDFS['subClassOf'], y.rdf_type))
        cls.du.add_statements(deets)
        # Also get all of the properites
        try:
            for x in cls.datatypeProperties:
                DatatypeProperty(cls,x)
        except AttributeError:
            pass
        except:
            traceback.print_exc()

        try:
            for x in cls.objectProperties:
                if isinstance(x,tuple):
                    ObjectProperty(cls,x[0], value_type=x[1])
                else:
                    ObjectProperty(cls,x)
        except AttributeError:
            pass
        except:
            traceback.print_exc()
        setattr(P, cls.__name__, cls)

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

