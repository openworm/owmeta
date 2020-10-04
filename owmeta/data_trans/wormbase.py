from rdflib.namespace import Namespace
import csv
from owmeta_core.datasource import Informational
from owmeta_core.data_trans.csv_ds import CSVDataSource, CSVDataTranslator
import re
import traceback


from .. import CONTEXT
from ..utils import normalize_cell_name
from ..channel import Channel, ExpressionPattern
from ..evidence import Evidence
from ..muscle import Muscle, BodyWallMuscle
from ..network import Network
from ..neuron import Neuron
from ..cell import Cell
from ..website import Website
from ..worm import Worm

from .common_data import DSMixin, DTMixin
from .data_with_evidence_ds import DataWithEvidenceDataSource


class WormbaseTextMatchCSVDataSource(DSMixin, CSVDataSource):
    class_context = CONTEXT

    initial_cell_column = Informational('Initial Cell Column',
                                        description='The index of the first column with a cell name',
                                        multiple=False)

    cell_type = Informational('Cell Type',
                              description='The type of cell to be produced',
                              multiple=False)


class WormbaseIonChannelCSVDataSource(DSMixin, CSVDataSource):
    class_context = CONTEXT

    csv_header = ['channel_name',
                  'gene_name',
                  'gene_WB_ID',
                  'expression_pattern',
                  'description']


class WormbaseIonChannelCSVTranslator(DTMixin, CSVDataTranslator):
    class_context = CONTEXT

    input_type = WormbaseIonChannelCSVDataSource
    output_type = DataWithEvidenceDataSource

    def translate(self, data_source):
        res = self.make_new_output((data_source,))
        with res.evidence_context(Evidence=Evidence, Website=Website) as ctx:
            doc = ctx.Website(key="wormbase", url="http://Wormbase.org", title="WormBase")
            doc_ctx = res.data_context_for(document=doc)
            ctx.Evidence(reference=doc, supports=doc_ctx.rdf_object)

        with self.make_reader(data_source) as csvreader:
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
        return res


class WormbaseTextMatchCSVTranslator(DTMixin, CSVDataTranslator):
    class_context = CONTEXT

    input_type = WormbaseTextMatchCSVDataSource
    output_type = DataWithEvidenceDataSource

    def translate(self, data_source):
        initcol = data_source.initial_cell_column()
        ctype = data_source.cell_type()

        ctype = self.context.resolve_class(ctype)

        res = self.make_new_output((data_source,))
        with res.evidence_context(Evidence=Evidence, Website=Website) as ctx:
            doc = ctx.Website(key="wormbase", url="http://Wormbase.org", title="WormBase")
            doc_ctx = res.data_context_for(document=doc)
            ctx.Evidence(reference=doc, supports=doc_ctx.rdf_object)

        with open(data_source.full_path(), 'r') as f:
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


class WormBaseCSVDataSource(DSMixin, CSVDataSource):
    class_context = CONTEXT

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


class CellWormBaseCSVTranslator(DTMixin, CSVDataTranslator):
    class_context = CONTEXT

    input_type = WormBaseCSVDataSource
    output_type = DataWithEvidenceDataSource

    def translate(self, data_source):
        """ Translate wormbase CSV dump into Cells, Neurons, and Muscles """
        res = self.make_new_output((data_source,))
        with self.make_reader(data_source, skipheader=False, skiplines=3,
                dict_reader=True,
                fieldnames=data_source.csv_header.one()) as csvreader:
            # TODO: Improve this evidence by going back to the actual research
            #       by using the wormbase REST API in addition to or instead of the CSV file
            with res.evidence_context(Evidence=Evidence, Website=Website) as ctx:
                doc = ctx.Website(key="wormbase", url="http://Wormbase.org", title="WormBase")
                doc_ctx = res.data_context_for(document=doc)
                ctx.Evidence(reference=doc, supports=doc_ctx.rdf_object)

            with doc_ctx(Worm=Worm,
                         BodyWallMuscle=BodyWallMuscle,
                         Muscle=Muscle,
                         Network=Network,
                         Neuron=Neuron,
                         Cell=Cell) as ctx:
                w = ctx.Worm()
                n = ctx.Network()
                n.worm(w)

                for line in csvreader:
                    cell = None
                    if line['Body wall muscles']:
                        cell = ctx.BodyWallMuscle()
                        w.muscle(cell)
                    elif line['Pharynx muscles'] or line['Other muscles']:
                        cell = ctx.Muscle()
                        w.muscle(cell)
                    elif line['Neurons (no male-specific cells)']:
                        cell = ctx.Neuron()
                        cell.wormbaseID(line['WormBase ID'])
                        n.neuron(cell)
                    elif (line['Other adult-only cells in the hermaphrodite'] or
                            line['Other adult-only hermaphrodite-specific cells (not present in males)']):
                        cell = ctx.Cell()

                    if cell:
                        cell.wormbaseID(line['WormBase ID'])
                        cell.name(normalize_cell_name(line['Cell']).upper())
                        cell.description(line['Description'])
                        w.cell(cell)
        return res
