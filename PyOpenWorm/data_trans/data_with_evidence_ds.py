from rdflib.namespace import Namespace
from ..context import Context
from ..contextDataObject import ContextDataObject
from ..datasource import Informational, DataSource
from .. import CONTEXT
from .common_data import DS_NS


class DataWithEvidenceDataSource(DataSource):
    evidence_context_property = Informational(display_name='Evidence context',
                                              property_name='evidence_context',
                                              description='The context in which evidence'
                                                          ' for the "Data context" is defined')
    data_context_property = Informational(display_name='Data context',
                                          property_name='data_context',
                                          description='The context in which primary data'
                                                      ' for this data source is defined')

    combined_context_property = Informational(display_name='Combined context',
                                              property_name='combined_context',
                                              description='Context importing both the data and evidence contexts')

    rdf_namespace = Namespace(DS_NS['DataWithEvidenceDataSource#'])

    def __init__(self, *args, **kwargs):
        super(DataWithEvidenceDataSource, self).__init__(*args, **kwargs)

        if self.defined:
            if not self.data_context_property.has_defined_value():
                self.data_context_property(ContextDataObject.contextualize(self.context)(self.identifier + '-data'))
            if not self.evidence_context_property.has_defined_value():
                self.evidence_context_property(ContextDataObject.contextualize(self.context)(self.identifier +
                                                                                             '-evidence'))
            if not self.combined_context.has_defined_value():
                self.combined_context_property(ContextDataObject.contextualize(self.context)(self.identifier))

        self.__ad_hoc_contexts = dict()

    @property
    def data_context(self):
        return Context.contextualize(self.context)(ident=self.identifier + '-data', imported=(CONTEXT,))

    @property
    def evidence_context(self):
        return Context.contextualize(self.context)(ident=self.identifier + '-evidence', imported=(CONTEXT,))

    @property
    def combined_context(self):
        return Context.contextualize(self.context)(ident=self.identifier, imported=(self.data_context,
                                                   self.evidence_context))

    def data_context_for(self, **kwargs):
        ctx = self.context_for(**kwargs)
        self.data_context.add_import(ctx)
        return ctx

    def context_for(self, **kwargs):
        key = "&".join(k + "=" + kwargs[k].identifier for k in sorted(kwargs.keys()))
        res = self.__ad_hoc_contexts.get(key)
        if res is None:
            ctxid = self.identifier + '/context_for?' + key
            self.__ad_hoc_contexts[key] = Context.contextualize(self.context)(ident=ctxid)
            res = self.__ad_hoc_contexts[key]
        return res

    def commit_augment(self):
        saved_contexts = set([])
        self.data_context.save_context(inline_imports=True, saved_contexts=saved_contexts)
        self.data_context.save_imports()
        self.evidence_context.save_context(inline_imports=True, saved_contexts=saved_contexts)
        self.evidence_context.save_imports()


__yarom_mapped_classes__ = (DataWithEvidenceDataSource,)
