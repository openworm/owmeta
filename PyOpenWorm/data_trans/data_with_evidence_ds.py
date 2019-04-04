from rdflib.namespace import Namespace
from ..context import Context
from ..contextDataObject import ContextDataObject
from ..datasource import Informational, DataSource
from .. import CONTEXT
from .common_data import DS_NS
from .context_datasource import VariableIdentifierContext


class DataWithEvidenceDataSource(DataSource):
    evidence_context_property = Informational(display_name='Evidence context',
                                              property_name='evidence_context',
                                              property_type='ObjectProperty',
                                              description='The context in which evidence'
                                                          ' for the "Data context" is defined')

    data_context_property = Informational(display_name='Data context',
                                          property_name='data_context',
                                          property_type='ObjectProperty',
                                          description='The context in which primary data'
                                                      ' for this data source is defined')

    combined_context_property = Informational(display_name='Combined context',
                                              property_name='combined_context',
                                              property_type='ObjectProperty',
                                              description='Context importing both the data and evidence contexts')

    rdf_namespace = Namespace(DS_NS['DataWithEvidenceDataSource#'])

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
            self.data_context_property(self.data_context.rdf_object)
            self.evidence_context_property(self.evidence_context.rdf_object)
            self.combined_context_property(self.combined_context.rdf_object)

    def data_context_for(self, **kwargs):
        ctx = self.context_for(**kwargs)
        self.data_context.add_import(ctx)
        return ctx

    def context_for(self, ident=None, **kwargs):
        key = "&".join(k + "=" + kwargs[k].identifier for k in sorted(kwargs.keys()))
        res = self.__ad_hoc_contexts.get(key)
        if res is None:
            if ident:
                ctxid = ident
            else:
                ctxid = self.identifier + '/context_for?' + key
            self.__ad_hoc_contexts[key] = Context.contextualize(self.context)(ident=ctxid)
            res = self.__ad_hoc_contexts[key]
        return res

    def commit_augment(self):
        saved_contexts = set([])
        self.data_context.save_context(inline_imports=True, saved_contexts=saved_contexts)
        self.evidence_context.save_context(inline_imports=True, saved_contexts=saved_contexts)
        self.combined_context.save_imports()


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


__yarom_mapped_classes__ = (DataWithEvidenceDataSource,)
