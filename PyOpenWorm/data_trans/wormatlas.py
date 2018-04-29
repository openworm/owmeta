import traceback

from ..datasource import Translation
from ..network import Network
from ..worm import Worm
from ..website import Website

from rdflib.namespace import Namespace
from .csv_ds import CSVDataSource, CSVDataTranslator
from .data_with_evidence_ds import DataWithEvidenceDataSource
from .common_data import DS_NS, TRANS_NS


class WormAtlasCellListDataSource(CSVDataSource):
    rdf_namespace = Namespace(DS_NS['WormAtlasCellListDataSource#'])
    csv_header = ['Cell', 'Lineage Name', 'Description']
    csv_field_delimiter = '\t'


class WormAtlasCellListDataTranslation(Translation):
    def __init__(self, **kwargs):
        super(WormAtlasCellListDataTranslation, self).__init__(**kwargs)
        self.neurons_source = WormAtlasCellListDataTranslation.ObjectProperty()


class WormAtlasCellListDataTranslator(CSVDataTranslator):
    input_type = (WormAtlasCellListDataSource, DataWithEvidenceDataSource)
    output_type = DataWithEvidenceDataSource
    translation_type = WormAtlasCellListDataTranslation
    translator_identifier = TRANS_NS.WormAtlasCellListDataTranslator

    def translate(self, data_source, neurons_source):
        # XXX: This wants a way to insert cells, then later, to insert neurons from the same set
        # and have the later recoginzed as the former. Identifier matching limits us here. It would
        # be best to establish owl:sameAs links to the super class (Cell) from the subclass (Neuron)
        # at the sub-class insert and have a reasoner relate
        # the two sets of inserts.
        res = self.make_new_output(sources=(data_source, neurons_source))
        tr = res.translation.onedef()
        tr.neurons_source(neurons_source)
        try:
            net_q = neurons_source.data_context.query(Network)()
            net = next(net_q.load(), net_q)

            # TODO: Improve this evidence marker
            doc = res.evidence_context(Website)(url="http://www.wormatlas.org/celllist.htm")
            doc_ctx = res.data_context_for(document=doc)
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
            # Also requires removing neurons and muscles from the list once
            # they've been identified so they aren't stored twice

            print ("uploaded lineage and descriptions")
        except Exception:
            traceback.print_exc()
        return res


__yarom_mapped_classes__ = (WormAtlasCellListDataSource,
                            WormAtlasCellListDataTranslator,
                            WormAtlasCellListDataTranslation)
