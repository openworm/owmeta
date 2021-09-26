from owmeta_core.datasource import Informational, DataTranslator, DataSource
from owmeta_core.data_trans.local_file_ds import LocalFileDataSource
from owmeta_core.data_trans.context_datasource import VariableIdentifierContext

from .. import CONTEXT, SCI_CTX
from ..bibtex import parse_bibtex_into_evidence

from .common_data import DSMixin, DTMixin


class EvidenceDataSource(DSMixin, DataSource):
    class_context = SCI_CTX

    context_property = Informational(display_name='Context',
                                     property_name='evidence_context',
                                     property_type='ObjectProperty',
                                     description='The context')

    def __init__(self, *args, **kwargs):
        super(EvidenceDataSource, self).__init__(*args, **kwargs)
        self.context = _EvidenceContext.contextualize(self.context)(maker=self,
                                                                    imported=(CONTEXT,))
        self.context_property(self.evidence_context.rdf_object)

    def after_transform(self):
        super(EvidenceDataSource, self).after_transform()
        saved_contexts = set([])
        self.data_context.save_context(inline_imports=True, saved_contexts=saved_contexts)
        self.context.save_context(inline_imports=True, saved_contexts=saved_contexts)
        self.context.save_imports()


class _EvidenceContext(VariableIdentifierContext):
    def identifier_helper(self):
        return self.maker.identifier + '-evidence'


class BibTexDataSource(DSMixin, LocalFileDataSource):
    class_context = SCI_CTX

    def __init__(self, bibtex_file_name, **kwargs):
        super(BibTexDataSource, self).__init__(**kwargs)
        self.bibtex_file_name = bibtex_file_name


class BibTexDataTranslator(DTMixin, DataTranslator):
    class_context = SCI_CTX

    input_type = BibTexDataSource
    output_type = EvidenceDataSource

    def translate(data_source):
        evidences = parse_bibtex_into_evidence(data_source.bibtex_file_name)
        return evidences.values()
