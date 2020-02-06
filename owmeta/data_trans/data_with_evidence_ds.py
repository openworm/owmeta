from rdflib.namespace import Namespace
from owmeta_core.context import Context
from owmeta_core.contextDataObject import ContextDataObject
from owmeta_core.datasource import Informational, DataSource
from owmeta_core.mapper import mapped
from owmeta_core.data_trans.context_datasource import VariableIdentifierContext
from .. import CONTEXT
from .common_data import DS_NS


@mapped
class DataWithEvidenceDataSource(DataSource):
    evidence_context_property = Informational(display_name='Evidence context',
                                              property_name='evidence_context',
                                              property_type='ObjectProperty',
                                              multiple=False,
                                              description='The context in which evidence'
                                                          ' for the "Data context" is defined')

    data_context_property = Informational(display_name='Data context',
                                          property_name='data_context',
                                          property_type='ObjectProperty',
                                          multiple=False,
                                          description='The context in which primary data'
                                                      ' for this data source is defined')

    combined_context_property = Informational(display_name='Combined context',
                                              property_name='combined_context',
                                              property_type='ObjectProperty',
                                              multiple=False,
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
        self.combined_context.save(inline_imports=True)
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
