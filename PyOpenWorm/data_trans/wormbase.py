from rdflib.namespace import Namespace
import csv
import re
import traceback

from ..utils import normalize_cell_name
from ..channel import Channel, ExpressionPattern
from ..evidence import Evidence
from ..muscle import Muscle
from ..network import Network
from ..neuron import Neuron
from ..website import Website
from ..worm import Worm
from ..datasource import Informational

from .common_data import DS_NS, TRANS_NS
from .csv_ds import CSVDataSource, CSVDataTranslator
from .data_with_evidence_ds import DataWithEvidenceDataSource


class WormbaseTextMatchCSVDataSource(CSVDataSource):
    rdf_namespace = Namespace(DS_NS['WormbaseTextMatchCSVDataSource#'])

    initial_cell_column = Informational('Initial Cell Column',
                                        description='The index of the first column with a cell name',
                                        multiple=False)

    cell_type = Informational('Cell Type',
                              description='The type of cell to be produced',
                              multiple=False)


class WormbaseIonChannelCSVDataSource(CSVDataSource):

    rdf_namespace = Namespace(DS_NS['WormbaseIonChannelCSVDataSource#'])

    csv_header = ['channel_name',
                  'gene_name',
                  'gene_WB_ID',
                  'expression_pattern',
                  'description']


class WormbaseIonChannelCSVTranslator(CSVDataTranslator):
    input_type = WormbaseIonChannelCSVDataSource
    output_type = DataWithEvidenceDataSource
    translator_identifier = TRANS_NS.WormbaseIonChannelCSVTranslator

    def translate(self, data_source):
        res = self.make_new_output((data_source,))
        try:
            with res.evidence_context(Evidence=Evidence, Website=Website) as ctx:
                doc = ctx.Website(key="wormbase", url="http://Wormbase.org", title="WormBase")
                doc_ctx = res.data_context_for(document=doc)
                ctx.Evidence(reference=doc, supports=doc_ctx.rdf_object)

            with open(data_source.csv_file_name.onedef(), 'r') as csvfile:
                next(csvfile, None)
                csvreader = csv.reader(csvfile, skipinitialspace=True)
                with doc_ctx(Channel=Channel,
                             ExpressionPattern=ExpressionPattern) as ctx:
                    for line in csvreader:
                        channel_name = normalize_cell_name(line[0]).upper()
                        gene_name = line[1].upper()
                        gene_WB_ID = line[2].upper()
                        expression_pattern = line[3]
                        description = line[4]
                        c = ctx.Channel(name=str(channel_name))
                        c.gene_name(gene_name)
                        c.gene_WB_ID(gene_WB_ID)
                        c.description(description)
                        patterns = expression_pattern.split(r' | ')
                        regex = re.compile(r' *\[([^\]]+)\] *(.*) *')

                        matches = [regex.match(pat) for pat in patterns]
                        patterns = [ctx.ExpressionPattern(wormbaseid=m.group(1),
                                                          description=m.group(2))
                                    for m in matches if m is not None]
                        for pat in patterns:
                            c.expression_pattern(pat)
        except Exception:
            traceback.print_exc()
        return res


class WormbaseTextMatchCSVTranslator(CSVDataTranslator):
    input_type = WormbaseTextMatchCSVDataSource
    output_type = DataWithEvidenceDataSource
    translator_identifier = TRANS_NS.WormbaseTextMatchCSVTranslator

    def translate(self, data_source):
        initcol = data_source.initial_cell_column()
        ctype = data_source.cell_type()

        ctype = self.context.resolve_class(ctype)

        res = self.make_new_output((data_source,))
        try:
            with res.evidence_context(Evidence=Evidence, Website=Website) as ctx:
                doc = ctx.Website(key="wormbase", url="http://Wormbase.org", title="WormBase")
                doc_ctx = res.data_context_for(document=doc)
                ctx.Evidence(reference=doc, supports=doc_ctx.rdf_object)

            with open(data_source.csv_file_name.one(), 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                header = self.skip_to_header(reader)
                with doc_ctx(Channel=Channel, CType=ctype) as ctx:
                    for row in reader:
                        cells = self.extract_cell_names(header,
                                                        initcol,
                                                        row)
                        ch = ctx.Channel(name=str(row[0]))
                        for cell in cells:
                            m = ctx.CType(name=str(cell))
                            ch.appearsIn(m)
        except Exception:
            traceback.print_exc()
        return res

    def skip_to_header(self, reader):
        rows = 0
        for row in reader:
            if rows == 3:
                return row
            rows += 1
        return None

    def extract_cell_names(self, header, initial_cell_column, row):
        res = []
        cols = 0
        for col in row:
            if cols > initial_cell_column:
                if col == '1' or col == '2':
                    res.append(header[cols])
            cols += 1
        return res


class WormBaseCSVDataSource(CSVDataSource):
    rdf_namespace = Namespace(DS_NS['MuscleCSVDataSource#'])
    csv_header = ["Cell",
                  "Lineage Name",
                  "Description",
                  "Total count of identified adult-only hermaphrodite cells",
                  "Total count of adult-only male cells",
                  "Neurons (no male-specific cells)",
                  "Neurons (male-specific)",
                  "Body wall muscles",
                  "Pharynx muscles",
                  "Other muscles",
                  "Other adult-only cells in the hermaphrodite",
                  "Other adult-only hermaphrodite-specific cells (not present in males)",
                  "Motor neurons related to body wall muscles",
                  "Embryonic cells not present in adult",
                  "Male-specific cells",
                  "Male-specific adult-only cells",
                  "Cells with non-unique name",
                  "",
                  "VirtualWorm blender model names",
                  "WormBase ID",
                  "Synonyms"]


class MuscleWormBaseCSVTranslator(CSVDataTranslator):
    input_type = WormBaseCSVDataSource
    output_type = DataWithEvidenceDataSource
    translator_identifier = TRANS_NS.MuscleWormBaseCSVTranslator

    def translate(self, data_source):
        """ Upload muscles and the neurons that connect to them """
        res = self.make_new_output((data_source,))
        with open(data_source.csv_file_name.onedef()) as csvfile:
            csvreader = csv.reader(csvfile)

            # TODO: Improve this evidence by going back to the actual research
            #       by using the wormbase REST API in addition to or instead of the CSV file
            with res.evidence_context(Evidence=Evidence, Website=Website) as ctx:
                doc = ctx.Website(key="wormbase", url="http://Wormbase.org", title="WormBase")
                doc_ctx = res.data_context_for(document=doc)
                ctx.Evidence(reference=doc, supports=doc_ctx.rdf_object)

            with doc_ctx(Worm=Worm, Muscle=Muscle) as ctx:
                w = ctx.Worm()

                for num, line in enumerate(csvreader):
                    if num < 4:  # skip rows with no data
                        continue

                    if line[7] or line[8] or line[9] == '1':  # muscle's marked in these columns
                        muscle_name = normalize_cell_name(line[0]).upper()
                        m = ctx.Muscle(name=muscle_name)
                        w.muscle(m)
        return res


class NeuronWormBaseCSVTranslator(CSVDataTranslator):
    input_type = WormBaseCSVDataSource
    output_type = DataWithEvidenceDataSource
    translator_identifier = TRANS_NS.NeuronWormBaseCSVTranslator

    def translate(self, data_source):
        res = self.make_new_output((data_source,))
        # TODO: Improve this evidence by going back to the actual research
        #       by using the wormbase REST API in addition to or instead of the CSV file
        with res.evidence_context(Evidence=Evidence, Website=Website) as ctx:
            doc = ctx.Website(key="wormbase", url="http://Wormbase.org", title="WormBase")
            doc_ctx = res.data_context_for(document=doc)
            ctx.Evidence(reference=doc, supports=doc_ctx.rdf_object)

        with doc_ctx(Worm=Worm, Network=Network, Neuron=Neuron) as ctx:
            w = ctx.Worm()
            n = ctx.Network()
            n.worm(w)

            with open(data_source.csv_file_name.one()) as csvfile:
                csvreader = csv.reader(csvfile)

                for num, line in enumerate(csvreader):
                    if num < 4:  # skip rows with no data
                        continue

                    if line[5] == '1':  # neurons marked in this column
                        neuron_name = normalize_cell_name(line[0]).upper()
                        n.neuron(ctx.Neuron(name=neuron_name))
        return res


__yarom_mapped_classes__ = (WormbaseTextMatchCSVDataSource,
                            WormbaseIonChannelCSVDataSource,
                            WormbaseIonChannelCSVTranslator,
                            WormbaseTextMatchCSVTranslator,
                            WormBaseCSVDataSource,
                            MuscleWormBaseCSVTranslator,
                            NeuronWormBaseCSVTranslator)
