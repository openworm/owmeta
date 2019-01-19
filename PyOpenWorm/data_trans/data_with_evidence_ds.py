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
                self.data_context_property(ContextDataObject.contextualize(self.context)(ident=self.identifier +
                                                                                         '-data'))
            if not self.evidence_context_property.has_defined_value():
                self.evidence_context_property(ContextDataObject.contextualize(self.context)(ident=self.identifier +
                                                                                             '-evidence'))
            if not self.combined_context_property.has_defined_value():
                self.combined_context_property(ContextDataObject.contextualize(self.context)(ident=self.identifier))

        self.__ad_hoc_contexts = dict()

        self.data_context = _DataContext.contextualize(self.context)(maker=self,
                                                                     imported=(CONTEXT,))

        self.evidence_context = _EvidenceContext.contextualize(self.context)(maker=self,
                                                                             imported=(CONTEXT,))

        self.combined_context = _CombinedContext.contextualize(self.context)(maker=self,
                                                                             imported=(self.data_context,
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
        self.evidence_context.save_context(inline_imports=True, saved_contexts=saved_contexts)
        self.combined_context.save_imports()


class _SContext(Context):
    def __init__(self, maker, **kwargs):
        conf = kwargs.pop('conf', maker.conf)
        super(_SContext, self).__init__(conf=conf, **kwargs)
        self.maker = maker

    @property
    def identifier(self):
        return self.identifier_helper()

    @identifier.setter
    def identifier(self, a):
        pass


class _CombinedContext(_SContext):
    def identifier_helper(self):
        return self.maker.identifier


class _EvidenceContext(_SContext):
    def identifier_helper(self):
        return self.maker.identifier + '-evidence'


class _DataContext(_SContext):
    def identifier_helper(self):
        return self.maker.identifier + '-data'


__yarom_mapped_classes__ = (DataWithEvidenceDataSource,)
