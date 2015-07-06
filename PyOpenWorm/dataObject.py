import rdflib as R
import random as RND
from yarom.graphObject import GraphObject, ComponentTripler
from PyOpenWorm.v0.dataObject import DataObject as DO
from .simpleProperty import SimpleProperty
from graphObjectAdapter.fakeProperty import FakeProperty

_DataObjects = dict()


class DataObject(GraphObject, DO):

    """ Adapts a DataObject to the GraphObject interface """

    def __init__(self, *args, **kwargs):
        key = None
        if 'key' in kwargs:
            key = kwargs['key']
            del kwargs['key']
        GraphObject.__init__(self)
        DO.__init__(self, *args, **kwargs)
        self._variable = R.Variable("V" + str(RND.random()))
        self.setKey(key)

    def __repr__(self):
        s = self.__class__.__name__ + "("
        if self._id is not None:
            s += self._id
        s += ")"
        return s

    def setKey(self, key):
        if isinstance(key, str):
            self._id = self.make_identifier_direct(key)
        else:
            self._id = self.make_identifier(key)

    @classmethod
    def make_identifier_direct(cls, string):
        if not isinstance(string, str):
            raise Exception("make_identifier_direct only accepts strings")
        from urllib import quote
        return R.URIRef(cls.rdf_namespace[quote(string)])

    def triples(self, *args, **kwargs):
        return ComponentTripler(self)()

    def __str__(self):
        return str(self.idl)

    def identifier(self, query=False):
        return DO.identifier(self)

    @property
    def defined(self):
        return (self.identifier() is not None)

    def variable(self):
        return self._variable

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
            link = owner_class.rdf_namespace[linkName]
            c = type(property_class_name,
                     (SimpleProperty,),
                     dict(linkName=linkName,
                          link=link,
                          property_type=property_type,
                          value_rdf_type=value_rdf_type,
                          owner_type=owner_class,
                          multiple=multiple))
            _DataObjects[property_class_name] = c
            c.register()
        # The fake property has the object as owner and the property as value
        res = c(owner=owner)
        # XXX: Hack for graph object traversal of properties while still
        #      allowing to refer to the PyOpenWorm properties.

        fp = FakeProperty(res)
        # ... and the properties of the owner only list the FakeProperty
        owner.properties.append(fp)
        setattr(owner, linkName, res)

        return res
