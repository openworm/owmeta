from ..datasource import DataTranslator, OneOrMore
from .common_data import TRANS_NS
from .data_with_evidence_ds import DataWithEvidenceDataSource


class ContextMergeDataTranslator(DataTranslator):
    translator_identifier = TRANS_NS.ContextMergeDataTranslator
    input_type = OneOrMore(DataWithEvidenceDataSource)
    output_type = DataWithEvidenceDataSource

    def translate(self, *sources):
        if not sources:
            raise Exception("No sources were provided")

        sources = sorted(sources, key=lambda s: s.identifier)
        res = self.make_new_output(sources=sources)

        for src in sources:
            res.data_context.add_import(src.data_context)
            res.evidence_context.add_import(src.evidence_context)
        return res


__yarom_mapped_classes__ = (ContextMergeDataTranslator,)
