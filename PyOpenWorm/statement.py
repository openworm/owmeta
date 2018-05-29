import logging

from yarom.mapper import FCN

L = logging.getLogger(__name__)


class Statement(object):
    __slots__ = ('subject', 'property', 'object', 'context')

    def __init__(self, subj, prop, obj, context):
        self.subject = subj
        self.property = prop
        self.object = obj
        self.context = context

    def contextualize(self, context):
        return Statement(self.subject, self.property, self.object, context)

    def to_quad(self):
        return (self.subject.idl,
                self.property.link,
                self.object.idl,
                self.context.identifier if self.context is not None else None)

    def to_triple(self):
        return (self.subject.idl, self.property.link, self.object.idl)

    def __hash__(self):
        return (3706407563 ^
                hash(self.subject.idl) ^
                hash(self.property.link) ^
                hash(self.object.idl) ^
                hash(self.context.identifier if self.context is not None else None))

    def __eq__(self, other):
        return (self.subject.idl == other.subject.idl and
                self.property.link == other.property.link and
                self.object.idl == other.object.idl and
                (self.context is None and other.context is None or
                    self.context.identifier == other.context.identifier))

    def __repr__(self):
        return '{}(subj={}, prop={}, obj={}, context={})'.format(FCN(type(self)),
                                                                 repr(self.subject),
                                                                 repr(self.property),
                                                                 repr(self.object),
                                                                 repr(self.context))

    def __getitem__(self, idx):
        if idx == 0:
            return self.subject
        elif idx == 1:
            return self.property
        elif idx == 2:
            return self.object
        elif idx == 3:
            return self.context
        else:
            raise IndexError
