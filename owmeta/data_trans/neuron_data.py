from rdflib.namespace import Namespace

from ..neuron import Neuron
from ..network import Network
from ..worm import Worm
from ..document import Document
from ..evidence import Evidence
from ..bibtex import parse_bibtex_into_documents
from ..datasource import Informational
from .common_data import DS_NS, TRANS_NS
from .csv_ds import CSVDataSource, CSVDataTranslator

from .data_with_evidence_ds import DataWithEvidenceDataSource


class NeuronCSVDataSource(CSVDataSource):
    rdf_namespace = Namespace(DS_NS['NeuronCSVDataSource#'])
    bibtex_files = Informational(display_name='BibTeX files',
                                 description='List of BibTeX files that are referenced in the csv file by entry ID')


class NeuronCSVDataTranslator(CSVDataTranslator):
    input_type = NeuronCSVDataSource
    output_type = DataWithEvidenceDataSource
    translator_identifier = TRANS_NS.NeuronCSVDataTranslator

    def __init__(self, *args, **kwargs):
        super(NeuronCSVDataTranslator, self).__init__(*args, **kwargs)
        self.__document_contexts = dict()

    def translate(self, data_source):
        res = self.make_new_output((data_source,))

        documents = dict()
        bibtex_files = data_source.bibtex_files.onedef()
        if bibtex_files is not None:
            for bib in bibtex_files:
                documents.update(parse_bibtex_into_documents(bib, res.evidence_context))
        worm = res.data_context(Worm)()
        network = res.data_context(Network)(worm=worm)
        with self.make_reader(data_source, skipheader=True) as reader:
            for row in reader:
                neuron_name, relation, data, evidence, documentURL = row
                relation = relation.lower()

                docs = []
                doc = documents.get(evidence, None)
                if doc is not None:
                    docs.append(doc)

                if len(documentURL) > 0:
                    doc1 = documents.get(documentURL, res.evidence_context(Document)(uri=documentURL))
                    documents[documentURL] = doc1
                    docs.append(doc1)

                if relation in ('neurotransmitter', 'innexin', 'neuropeptide', 'receptor'):
                    for d in docs:
                        neu = res.data_context_for(document=d)(Neuron)(neuron_name)
                        network.neuron(neu)
                        getattr(neu, relation)(data)
                elif relation == 'type':
                    _data = data.lower()
                    # type data aren't normalized so we check for strings within the _data string
                    types = [x for x in ('sensory', 'interneuron', 'motor', 'unknown') if x in _data]

                    for t in types:
                        for d in docs:
                            neu = res.data_context_for(document=d)(Neuron)(neuron_name)
                            network.neuron(neu)
                            neu.type(t)
        for d in documents.values():
            contextualized_doc_ctx = res.evidence_context(res.data_context_for(document=d))
            res.evidence_context(Evidence)(reference=d, supports=contextualized_doc_ctx.rdf_object)
            res.data_context.add_import(contextualized_doc_ctx)
        return res


__yarom_mapped_classes__ = (NeuronCSVDataSource, NeuronCSVDataTranslator)
