from rdflib.namespace import Namespace
from ..bibtex import parse_bibtex_into_evidence
from ..datasource import Informational, DataTranslator, DataSource
from .local_file_ds import LocalFileDataSource
from ..context import Context
from ..contextDataObject import ContextDataObject
from .. import CONTEXT
from .common_data import DS_NS
from .context_datasource import VariableIdentifierContext, VariableIdentifierContextDataObject


class EvidenceDataSource(DataSource):
    context_property = Informational(display_name='Context',
                                     property_name='evidence_context',
                                     property_type='ObjectProperty',
                                     description='The context')

    rdf_namespace = Namespace(DS_NS['EvidenceDataSource#'])

    def __init__(self, *args, **kwargs):
        super(EvidenceDataSource, self).__init__(*args, **kwargs)
        self.context = _EvidenceContext.contextualize(self.context)(maker=self,
                                                                    imported=(CONTEXT,))
        self.context_property(self.evidence_context.rdf_object)

    def commit_augment(self):
        saved_contexts = set([])
        self.data_context.save_context(inline_imports=True, saved_contexts=saved_contexts)
        self.context.save_context(inline_imports=True, saved_contexts=saved_contexts)
        self.context.save_imports()


class _EvidenceContext(VariableIdentifierContext):
    def identifier_helper(self):
        return self.maker.identifier + '-evidence'


class BibTexDataSource(LocalFileDataSource):
    def __init__(self, bibtex_file_name, **kwargs):
        super(BibTexDataSource, self).__init__(**kwargs)
        self.bibtex_file_name = bibtex_file_name


class BibTexDataTranslator(DataTranslator):
    input_type = BibTexDataSource
    output_type = EvidenceDataSource

    def translate(data_source):
        evidences = parse_bibtex_into_evidence(data_source.bibtex_file_name)
        return evidences.values()


__yarom_mapped_classes__ = (BibTexDataSource, BibTexDataTranslator, EvidenceDataSource,)
