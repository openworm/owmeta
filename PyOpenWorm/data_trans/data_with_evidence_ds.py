from rdflib.namespace import Namespace
from PyOpenWorm.context import Context
from PyOpenWorm.datasource import Informational, DataSource
from PyOpenWorm import CONTEXT
from .common_data import DS_NS


class DataWithEvidenceDataSource(DataSource):
    evidence_context = Informational(display_name='Evidence context',
                                     description='The context in which evidence for the "Data context" is defined')
    data_context = Informational(display_name='Data context',
                                 description='The context in which primary data for this data source is defined')
    contexts = Informational(display_name='Other contexts',
                             description='Other contexts defined by the data translator')

    rdf_namespace = Namespace(DS_NS['DataWithEvidenceDataSource#'])

    def __init__(self, *args, **kwargs):
        super(DataWithEvidenceDataSource, self).__init__(*args, **kwargs)
        # print(self.translation._v)
        self.data_context = Context(ident=self.identifier + '-data',
                                    imported=(CONTEXT,))
        self.evidence_context = Context(ident=self.identifier + '-evidence',
                                        imported=(CONTEXT,))
        self.contexts = []


__yarom_mapped_classes__ = (DataWithEvidenceDataSource,)
