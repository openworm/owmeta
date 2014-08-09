import rdflib as R
from PyOpenWorm import DataUser
import PyOpenWorm as P
import traceback

__all__ = [ "DataObjectMapper", "_DataObjectsParents"]

_DataObjects = dict()
# TODO: Put the subclass relationships in the database
_DataObjectsParents = dict()

class DataObjectMapper(type,DataUser):
    def __init__(cls, name, bases, dct):
        bs = list(bases)
        bs.append(DataUser)
        type.__init__(cls,name,tuple(bs),dct)
        DataUser.__init__(cls, conf=False)
        cls.bones = []
        DataObjectMapper.register(cls)

    @classmethod
    def setUpDB(self):
        for x in _DataObjectsParents:
            for y in _DataObjectsParents[x]:
                 (_DataObjects[x].rdf_type, R.RDFS['subClassOf'], y.rdf_type)

    @classmethod
    def register(self,cls):
        _DataObjects[cls.__name__] = cls
        _DataObjectsParents[cls.__name__] = [x for x in cls.__bases__ if isinstance(x, self)]
        cls.parents = _DataObjectsParents[cls.__name__]
        cls.rdf_type = cls.conf['rdf.namespace'][cls.__name__]
        cls.rdf_namespace = R.Namespace(cls.rdf_type + "/")

        # Also get all of the properites
        try:
            for x in cls.datatypeProperties:
                print 'dp',self.DatatypeProperty(cls,x)
        except AttributeError:
            pass
        except:
            traceback.print_exc()

        try:
            for x in cls.objectProperties:
                if isinstance(x,tuple):
                    print 'dp',self.ObjectProperty(cls,x[0], value_type=x[1])
                else:
                    print 'dp',self.ObjectProperty(cls,x)
        except:
            pass

        setattr(P, cls.__name__, cls)

    @classmethod
    def DatatypeProperty(cls,*args,**kwargs):
        """ Create a SimpleProperty that has a simple type (string,number,etc) as its value

        Parameters
        ----------
        linkName : string
            The name of this Property.
        """
        return cls._create_property(*args,property_type='DatatypeProperty',**kwargs)

    @classmethod
    def ObjectProperty(cls, *args,**kwargs):
        """ Create a SimpleProperty that has a complex DataObject as its value

        Parameters
        ----------
        linkName : string
            The name of this Property.
        value_type : type
            The type of DataObject fro values of this property
        """
        return cls._create_property(*args,property_type='ObjectProperty',**kwargs)

    @classmethod
    def _create_property(cls, owner_class, linkName, property_type, value_type=False):
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

        print 'putting some bones on %s' % owner_class
        owner_class.bones.append(c)

        return c

