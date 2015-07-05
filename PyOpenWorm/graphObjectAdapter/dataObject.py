from yarom.graphObject import GraphObject
from PyOpenWorm.dataObject import DataObject as DO
from .simpleProperty import SimpleProperty
from .fakeProperty import FakeProperty

_DataObjects = dict()


class _FakeOwner(object):

    def __init__(self, real_owner):
        self.properties = []
        self.owner_properties = []
        self._real_owner = real_owner

    def __str__(self):
        return "_FakeOwner({})".format(str(self._real_owner))

    @property
    def defined(self):
        return self._real_owner.defined

    @property
    def idl(self):
        return self._real_owner.idl


class DataObject(GraphObject, DO):

    """ Adapts a DataObject to the GraphObject interface """

    def __init__(self, *args, **kwargs):
        GraphObject.__init__(self)
        DO.__init__(self, *args, **kwargs)

    def __repr__(self):
        s = self.__class__.__name__ + "("
        if self._id is not None:
            s += self._id
        s += ")"
        return s

    def __str__(self):
        return str(self.idl)

    def identifier(self):
        return DO.identifier(self)

    @property
    def defined(self):
        return (self.identifier() is not None)

    @property
    def variable(self):
        self._id_variable

    def __hash__(self):
        return hash(self.idl)

    @classmethod
    def _create_property(
            cls,
            linkName,
            owner,
            property_type,
            value_type=False,
            multiple=False):
        # XXX This should actually get called for all of the properties when
        #     their owner classes are defined. The initialization, however, must
        #     happen with the owner object's creation
        owner_class = cls
        owner_class_name = owner_class.__name__
        property_class_name = owner_class_name + "_" + linkName
        if not value_type:
            value_type = DataObject

        c = None
        if property_class_name in _DataObjects:
            c = _DataObjects[property_class_name]
        else:
            if property_type == 'ObjectProperty':
                value_rdf_type = value_type.rdf_type
            else:
                value_rdf_type = False
            c = type(property_class_name,
                     (SimpleProperty,),
                     dict(linkName=linkName,
                          property_type=property_type,
                          value_rdf_type=value_rdf_type,
                          owner_type=owner_class,
                          multiple=multiple))
            _DataObjects[property_class_name] = c
            c.register()
        res = c(owner=_FakeOwner(owner))
        fp = FakeProperty(res)
        print("creating " + linkName)
        owner.properties.append(fp)
        setattr(owner, linkName, fp)

        return res
