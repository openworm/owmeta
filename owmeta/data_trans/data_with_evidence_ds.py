from owmeta_core.context import Context
from owmeta_core.datasource import Informational, DataSource
from owmeta_core.data_trans.context_datasource import (VariableIdentifierContext,
        VariableIdentifierContextDataObject)

from .. import CONTEXT, SCI_CTX

from .common_data import DSMixin


class DataWithEvidenceDataSource(DSMixin, DataSource):
    '''
    A data source that has an "evidence context" containing statements which support those
    in its "data context". The data source also has a combined context which imports both
    the data and evidence contexts. The data and evidence contexts have identifiers based
    on the data source's identifier and the combined context has the same identifier as
    the data source.
    '''

    class_context = SCI_CTX

    evidence_context_property = Informational(display_name='Evidence context',
                                              property_name='evidence_context',
                                              property_type='ObjectProperty',
                                              multiple=False,
                                              value_type=VariableIdentifierContextDataObject,
                                              description='The context in which evidence'
                                                          ' for the "Data context" is defined')

    data_context_property = Informational(display_name='Data context',
                                          property_name='data_context',
                                          property_type='ObjectProperty',
                                          multiple=False,
                                          value_type=VariableIdentifierContextDataObject,
                                          description='The context in which primary data'
                                                      ' for this data source is defined')

    combined_context_property = Informational(display_name='Combined context',
                                              property_name='combined_context',
                                              property_type='ObjectProperty',
                                              multiple=False,
                                              value_type=VariableIdentifierContextDataObject,
                                              description='Context importing both the data and evidence contexts')

    def __init__(self, *args, **kwargs):
        super(DataWithEvidenceDataSource, self).__init__(*args, **kwargs)

        self.__ad_hoc_contexts = dict()

        self.data_context = _DataContext.contextualize(self.context)(maker=self,
                                                                     imported=(CONTEXT,))

        self.evidence_context = _EvidenceContext.contextualize(self.context)(maker=self,
                                                                             imported=(CONTEXT,))

        self.combined_context = _CombinedContext.contextualize(self.context)(maker=self,
                                                                             imported=(self.data_context,
                                                                                       self.evidence_context))
        if not type(self).query_mode:
            if not self.data_context_property.has_defined_value():
                self.data_context_property(self.data_context.rdf_object)

            if not self.evidence_context_property.has_defined_value():
                self.evidence_context_property(self.evidence_context.rdf_object)

            if not self.combined_context_property.has_defined_value():
                self.combined_context_property(self.combined_context.rdf_object)

    def data_context_for(self, **kwargs):
        ctx = self.context_for(**kwargs)
        self.data_context.add_import(ctx)
        return ctx

    def context_for(self, ident=None, **kwargs):
        key = "&".join(k + "=" + getattr(kwargs[k], 'identifier', str(kwargs[k]))
                       for k in sorted(kwargs.keys()))
        res = self.__ad_hoc_contexts.get(key)
        if res is None:
            if ident:
                ctxid = ident
            else:
                ctxid = self.identifier + '/context_for?' + key
            self.__ad_hoc_contexts[key] = Context.contextualize(self.context)(ident=ctxid)
            res = self.__ad_hoc_contexts[key]
        return res

    def after_transform(self):
        super(DataWithEvidenceDataSource, self).after_transform()
        for ctx in self.__ad_hoc_contexts.values():
            ctx.save()

        self.evidence_context.save()
        self.data_context.save()
        self.combined_context.save()

        for ctx in self.__ad_hoc_contexts.values():
            ctx.save_imports(transitive=False)

        self.evidence_context.save_imports(transitive=False)
        self.data_context.save_imports(transitive=False)
        self.combined_context.save_imports(transitive=False)


class _CombinedContext(VariableIdentifierContext):
    def identifier_helper(self):
        if self.maker.defined:
            return self.maker.identifier
        else:
            return None


class _EvidenceContext(VariableIdentifierContext):
    def identifier_helper(self):
        if self.maker.defined:
            return self.maker.identifier + '-evidence'
        else:
            return None


class _DataContext(VariableIdentifierContext):
    def identifier_helper(self):
        if self.maker.defined:
            return self.maker.identifier + '-data'
        else:
            return None
