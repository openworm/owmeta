import traceback

from ..datasource import GenericTranslation
from ..network import Network
from ..worm import Worm
from ..website import Website
from ..evidence import Evidence

from rdflib.namespace import Namespace
from .csv_ds import CSVDataSource, CSVDataTranslator
from .data_with_evidence_ds import DataWithEvidenceDataSource
from .common_data import DS_NS, TRANS_NS


class WormAtlasCellListDataSource(CSVDataSource):
    rdf_namespace = Namespace(DS_NS['WormAtlasCellListDataSource#'])
    csv_header = ['Cell', 'Lineage Name', 'Description']
    csv_field_delimiter = '\t'


class WormAtlasCellListDataTranslation(GenericTranslation):
    def __init__(self, **kwargs):
        super(WormAtlasCellListDataTranslation, self).__init__(**kwargs)
        self.neurons_source = WormAtlasCellListDataTranslation.ObjectProperty()

    def defined_augment(self):
        return super(WormAtlasCellListDataTranslation, self).defined_augment() and \
                self.neurons_source.has_defined_value()

    def identifier_augment(self):
        return self.make_identifier(super(WormAtlasCellListDataTranslation, self).identifier_augment().n3() +
                                    self.neurons_source.onedef().identifier.n3())


class WormAtlasCellListDataTranslator(CSVDataTranslator):
    input_type = (WormAtlasCellListDataSource, DataWithEvidenceDataSource)
    output_type = DataWithEvidenceDataSource
    translation_type = WormAtlasCellListDataTranslation
    translator_identifier = TRANS_NS.WormAtlasCellListDataTranslator

    def make_translation(self, sources):
        res = super(WormAtlasCellListDataTranslator, self).make_translation()
        res.source(sources[0])
        res.neurons_source(sources[1])
        return res

    def translate(self, data_source, neurons_source):
        res = self.make_new_output(sources=(data_source, neurons_source))
        try:
            net_q = neurons_source.data_context.query(Network)()
            net = next(net_q.load(), net_q)

            # TODO: Improve this evidence marker
            doc = res.evidence_context(Website)(url="http://www.wormatlas.org/celllist.htm")
            ev = res.evidence_context(Evidence)(reference=doc)
            doc_ctx = res.data_context_for(document=doc)
            ev.supports(doc_ctx.rdf_object)
            w = doc_ctx(Worm)()

            with self.make_reader(data_source, skipinitialspace=True, skipheader=True) as csvreader:
                cell_name_counters = dict()
                data = dict()
                for j in csvreader:
                    name = j[0]
                    lineageName = j[1]
                    desc = j[2]

                    # XXX: These renaming choices are arbitrary; may be inappropriate
                    if name == "DB1/3":
                        name = "DB1"
                    elif name == "DB3/1":
                        name = "DB3"
                    elif name == "AVFL/R":
                        if lineageName[0] == "W":
                            name = "AVFL"
                        elif lineageName[0] == "P":
                            name = "AVFR"

                    if name in cell_name_counters:
                        basename = name
                        while name in cell_name_counters:
                            cell_name_counters[basename] += 1
                            name = basename + "(" + str(cell_name_counters[basename]) + ")"
                    else:
                        cell_name_counters[name] = 0

                    data[name] = {"lineageName": lineageName, "desc": desc}

            for n in net.neurons():
                # Get the name of the neuron in its original context
                name = n.name.one()
                cell_data = data[str(name)]
                # Make statements in the result context
                nn = doc_ctx(n)
                nn.lineageName(cell_data['lineageName'])
                nn.description(cell_data['desc'])
                w.cell(nn)

            # TODO: Add data for other cells here. Requires relating named
            # muscle cells to their counterparts in the cell list (e.g. mu_bod(#))

            print ("uploaded lineage and descriptions")
        except Exception:
            traceback.print_exc()
        return res


__yarom_mapped_classes__ = (WormAtlasCellListDataSource,
                            WormAtlasCellListDataTranslator,
                            WormAtlasCellListDataTranslation)
