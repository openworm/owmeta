"""
For declaring inverse properties of GraphObjects
"""


InverseProperties = dict()


class InversePropertyMixin(object):
    """
    Mixin for inverse properties.

    Augments RealSimpleProperty methods to update inverse properties as well
    """

    def set(self, other):
        ip_key = (self.owner_type, self.linkName)
        ip = InverseProperties.get(ip_key)
        if ip:
            rhs_cls, rhs_linkName = ip.other(*ip_key)
            if isinstance(other, rhs_cls):
                rhs_prop = getattr(other.contextualize(self.context), rhs_linkName)
                super(InversePropertyMixin, rhs_prop).set(self.owner)
        return super(InversePropertyMixin, self).set(other)

    def unset(self, other):
        ip_key = (self.owner_type, self.linkName)
        ip = InverseProperties.get(ip_key)
        if ip:
            rhs_cls, rhs_linkName = ip.other(*ip_key)
            if isinstance(other, rhs_cls):
                rhs_prop = getattr(other, rhs_linkName)
                ctxd_rhs_prop = rhs_prop.contextualize(self.context)
                super(InversePropertyMixin, ctxd_rhs_prop).unset(self.owner)
        return super(InversePropertyMixin, self).unset(other)


class InverseProperty(object):

    def __init__(self, lhs_class, lhs_linkName, rhs_class, rhs_linkName):
        self.lhs_class = lhs_class
        self.rhs_class = rhs_class

        self.lhs_linkName = lhs_linkName
        self.rhs_linkName = rhs_linkName
        InverseProperties[(lhs_class, lhs_linkName)] = self
        InverseProperties[(rhs_class, rhs_linkName)] = self

    def other(self, cls, name):
        if issubclass(cls, self.lhs_class) and self.lhs_linkName == name:
            return (self.rhs_class, self.rhs_linkName)
        elif issubclass(cls, self.rhs_class) and self.rhs_linkName == name:
            return (self.lhs_class, self.lhs_linkName)
        raise InversePropertyException('The property ({}, {}) has no inverse in {}'.format(cls, name, self))

    def __repr__(self):
        return 'InverseProperty({},{},{},{})'.format(self.lhs_class,
                                                     self.lhs_linkName,
                                                     self.rhs_class,
                                                     self.rhs_linkName)


class InversePropertyException(Exception):
    pass
