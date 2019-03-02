from __future__ import absolute_import
from collections import namedtuple

from yarom.mapper import FCN


class Statement(namedtuple('Statement', ('subject', 'property', 'object', 'context'))):
    __slots__ = ()

    def contextualize(self, context):
        return Statement(self.subject, self.property, self.object, context)

    def to_quad(self):
        return (self.subject.idl,
                self.property.link,
                self.object.idl,
                self.context.identifier if self.context is not None else None)

    def to_triple(self):
        return (self.subject.idl, self.property.link, self.object.idl)

    def __repr__(self):
        return '{}(subj={}, prop={}, obj={}, context={})'.format(FCN(type(self)),
                                                                 repr(self.subject),
                                                                 repr(self.property),
                                                                 repr(self.object),
                                                                 repr(self.context))
