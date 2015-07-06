from PyOpenWorm.pProperty import Property

# Define a property by writing the get
class SimpleProperty(Property):
    """ A property that has one or more links to a literals or DataObjects """

    def __init__(self,**kwargs):
        if not hasattr(self,'linkName'):
            self.__class__.linkName = self.__class__.__name__ + "property"
        Property.__init__(self, name=self.linkName, **kwargs)
        self.value_property = SimpleProperty.rdf_namespace['value']

        # Values set on this property
        self._v = []

        # The variable to be used for querying this property
        self._var = None
        if (self.owner==False) and hasattr(self,'owner_type'):
            self.owner = self.owner_type()

        if self.owner != False:
            # XXX: Shouldn't be recreating this here...
            self.link = self.owner_type.rdf_namespace[self.linkName]

    def hasVariable(self):
        return (self._var is not None)

    def hasValue(self):
        """ Returns true if the ``Property`` has had ``load`` called previously and some value was available or if
        ``set`` has been called previously

        :return: True if this data object has a value, False if not.
        """
        return len(self._v) > 0

    def _get(self):
        for x in self._v:
            yield x

    def get(self):
        """ If the ``Property`` has had ``load`` or ``set`` called previously, returns
        the resulting values. Otherwise, queries the configured rdf graph for values
        which are set for the ``Property``'s owner.
        """
        import random as RND
        if self.id_is_variable():
            try:
                self._var = R.Variable("V"+str(int(RND.random() * 1E10)))
                gp = self.owner.graph_pattern(query=True)
                if self.property_type == 'DatatypeProperty':
                    q = u"SELECT DISTINCT {0} where {{ {1} . }}".format(self._var.n3(), gp)
                elif self.property_type == 'ObjectProperty':
                    q = "SELECT DISTINCT {0} {0}_type where {{ {{ {1} }} . {0} rdf:type {0}_type }} ORDER BY {0}".format(self._var.n3(), gp)
                else:
                    raise Exception("Inappropriate property type "+self.property_type+" in SimpleProperty::get")
            finally:
                self._var = None
            qres = self.rdf.query(q)
            if self.property_type == 'DatatypeProperty':
                for x in qres:
                    if x[0] is not None and not DataObject._is_variable(x[0]):
                        yield _rdf_literal_to_python(x[0])
            elif self.property_type == 'ObjectProperty':
                for x in _QueryResultsTypeResolver(self, qres)():
                    yield x
        else:
            for value in self.rdf.objects(self.identifier(query=False), self.value_property):
                if self.property_type == 'DatatypeProperty':
                    if value is not None and not DataObject._is_variable(value):
                        yield _rdf_literal_to_python(value)
                elif self.property_type == 'ObjectProperty':
                    constructed_qres = set()
                    for rdf_type in self.rdf.objects(value, R.RDF['type']):
                        constructed_qres.add((value, rdf_type))

                    for ob in _QueryResultsTypeResolver(self, constructed_qres)():
                        yield ob

    def set(self,v):
        import bisect
        bisect.insort(self._v, v)
        if self.property_type == 'ObjectProperty':
            v.owner_properties.append(self)

        self.add_statements([])

    def triples(self,*args,**kwargs):
        query=kwargs.get('query',False)
        visited_list = kwargs.get('visited_list', False)

        if visited_list == False:
            visited_list = set()

        if self in visited_list:
            return
        else:
            visited_list.add(self)

        ident = self.identifier(query=query)

        if kwargs.get('saving', False):
            yield (self.identifier(), R.RDF['type'], self.rdf_type)

        if len(self._v) > 0:
            for x in Property.triples(self,*args,**kwargs):
                yield x
            for x in self._v:
                try:
                    if self.property_type == 'DatatypeProperty':
                        if isinstance(x, R.term.Identifier):
                            yield (ident, self.value_property, x)
                        else:
                            yield (ident, self.value_property, R.Literal(x))
                    elif self.property_type == 'ObjectProperty':
                        yield (ident, self.value_property, x.identifier(query=query))
                        for t in x.triples(*args,**kwargs):
                            yield t
                except Exception:
                    traceback.print_exc()
        elif query==True:
            if self.hasVariable():
                yield (ident, self.value_property, self._var)

    def triples0(self,*args,**kwargs):
        query=kwargs.get('query',False)
        owner_id = self.owner.identifier(query=query)
        ident = self.identifier(query=query)


        if len(self._v) > 0:
            for x in Property.triples(self,*args,**kwargs):
                yield x
            yield (owner_id, self.link, ident)
            for x in self._v:
                try:
                    if self.property_type == 'DatatypeProperty':
                        yield (ident, self.value_property, R.Literal(x))
                    elif self.property_type == 'ObjectProperty':
                        yield (ident, self.value_property, x.identifier(query=query))
                        for t in x.triples(*args,**kwargs):
                            yield t
                except Exception:
                    traceback.print_exc()
        elif query==True:
            # XXX: Remove this and require that we have a variable in `self._v` before
            #      we release triples that contain variables of any kind
            gv = self._graph_variable(self.linkName)
            yield (owner_id, self.link, ident)
            yield (ident, self.value_property, gv)

    def load(self):
        """ Loads in values to this ``Property`` which have been set for the associated owner,
        or if the owner refers to an unspecified member of its class, loads values which could
        be set based on the constraints on the owner.
        """
        # This load is way simpler since we just need the values for this property
        gp = self.graph_pattern(query=True)
        q = "SELECT DISTINCT ?"+self.linkName+"  where { "+ gp +" . }"
        L.debug('load_query='+q)
        qres = self.conf['rdf.graph'].query(q)
        for k in qres:
            k = k[0]
            value = False
            if not self._is_variable(k):
                if self.property_type == 'ObjectProperty':
                    value = self.object_from_id(k)
                elif self.property_type == 'DatatypeProperty':
                    value = str(k)

                if value:
                    self._v.append(value)
        yield self

    def identifier(self,query=False):
        """ Return the URI for this object

        Parameters
        ----------
        query: bool
            Indicates whether the identifier is to be used in a query or not
        """
        ident = DataObject.identifier(self,query=query)
        if self._id_is_set:
            return ident

        if query:
            # If we're querying then our identifier should be a variable if either our value is empty
            # or our owner's identifier is a variable
            owner_id = self.owner.identifier(query=query)
            vlen = len(self._v)
            if vlen == 0 or DataObject._is_variable(owner_id):
                return ident

        # Intentional fall through from if statement ...
        value_data = ""
        if self.property_type == 'DatatypeProperty':
            value_data = "".join(str(x) for x in self._v)
        elif self.property_type == 'ObjectProperty':
            for value in self._v:
                if not isinstance(value, DataObject):
                    raise Exception("Values for an ObjectProperty ({}) must be DataObjects. Given '{}'.".format(self, value))
            value_data = "".join(str(x.identifier()) for x in self._v if self is not x)

        return self.make_identifier((str(self.owner.identifier(query=False)), self.link, value_data))

    def __str__(self):
        return unicode(self.linkName + "=" + unicode(";".join(u"`{}'".format(unicode(x)) for x in set(self._v))))

