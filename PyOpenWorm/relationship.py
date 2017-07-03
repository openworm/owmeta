from .dataObject import DataObject


class Relationship(DataObject):

    """ A Relationship is typically related to a property and is an object that
        one points to for talking about the property relationship.

        For SimpleProperty objects, this acts like a RDF Reified triple.
        """

    def __init__(self, s=None, p=None, o=None, **kwargs):
        super(Relationship, self).__init__(**kwargs)
        Relationship.DatatypeProperty('subject', owner=self, multiple=False)
        Relationship.DatatypeProperty('property', owner=self, multiple=False)
        Relationship.DatatypeProperty('object', owner=self, multiple=False)
        if s is not None:
            self.subject(s)
        if p is not None:
            self.property(p)
        if o is not None:
            self.object(o)

    @property
    def defined(self):
        return (super(Relationship, self).defined or
                (self.subject.has_defined_value() and
                    self.property.has_defined_value() and
                    self.object.has_defined_value()))

    def identifier(self):
        if super(Relationship, self).defined:
            return super(Relationship, self).identifier()
        else:
            data = (self.subject,
                    self.property,
                    self.object)
            data = "".join(x.defined_values[0].identifier().n3() for x in data)
            return self.make_identifier(data)

    def __repr__(self):
        s = "Relationship("
        flip = False
        for x in ('subject', 'property', 'object'):
            if getattr(self, x).has_defined_value():
                if flip:
                    s += ", "
                s += x[0] + "=" + repr(getattr(self, x).defined_values[0].idl)
                flip = True
        s += ")"
        return s
