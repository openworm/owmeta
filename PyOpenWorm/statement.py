
class Statement(object):
    __slots__ = ('subject', 'property', 'object', 'context')

    def __init__(self, subj, prop, obj, context):
        self.subject = subj
        self.property = prop
        self.object = obj
        self.context = context

        if context is not None:
            self.context.add_statement(self)

    def contextualize(self, context):
        return Statement(self.subject, self.property, self.object, context)

    def __hash__(self):
        return 3706407563 ^ hash(self.subject.idl) ^ hash(self.property.link) ^ hash(self.context.identifier)

    def __eq__(self, other):
        return (self.subject.idl == other.subject.idl
                and self.property.link == other.property.link
                and self.object.idl == other.object.idl
                and self.context.identifier == other.context.identifier)

    def __repr__(self):
        return 'Statement(subj={}, prop={}, obj={}, context={})'.format(repr(self.subject),
                                                                        repr(self.property),
                                                                        repr(self.object),
                                                                        repr(self.context))
