from .muscle import Muscle
from .neuron import Neuron
from .data_trans.neuron_data import NeuronCSVDataSource
from .data_trans.wormatlas import WormAtlasCellListDataSource
from .data_trans.wormbase import (WormBaseCSVDataSource, WormbaseIonChannelCSVDataSource,
                                  WormbaseTextMatchCSVDataSource)
from .data_trans.connections import ConnectomeCSVDataSource


def owm_data(ns):
    '''
    Sources based on objects external to owmeta (e.g., files, websites)
    '''
    ctx = ns.context
    ctx.add_import(ConnectomeCSVDataSource.definition_context)

    ctx(ConnectomeCSVDataSource)(
            key='connectome',
            csv_file_name="connectome.csv")
    ctx(NeuronCSVDataSource)(
            key='bently_expression',
            csv_file_name="expression_data/Bentley_et_al_2016_expression.csv")
    ctx(NeuronCSVDataSource)(
            key='neurons',
            csv_file_name="Modified celegans db dump.csv",
            bibtex_files=["bibtex_files/altun2009.bib", "bibtex_files/WormAtlas.bib"])
    ctx(WormAtlasCellListDataSource)(
            key='cells',
            csv_file_name="C. elegans Cell List - WormAtlas.tsv",
            description="CSV converted from this Google Spreadsheet: "
            "https://docs.google.com/spreadsheets/d/"
            "1Jc9pOJAce8DdcgkTgkUXafhsBQdrer2Y47zrHsxlqWg/edit")
    ctx(WormbaseIonChannelCSVDataSource)(
            key='ion_channels',
            csv_file_name="ion_channel.csv",
            description="C. elegans ion channel data from WormBase. Contains"
            " WormBase IDs (WBIDs) for genes that code the ion channels and for"
            " the expression of those genes in C. elegans (e.g.,"
            " \"Chronogram479\", \"Expr6468\")")
    ctx(WormbaseTextMatchCSVDataSource)(
            key='muscle_ion_channels',
            csv_file_name="Ion channels - Ion Channel To Body Muscle.tsv",
            cell_type=Muscle.rdf_type,
            initial_cell_column=6)
    ctx(WormbaseTextMatchCSVDataSource)(
            key='neuron_ion_channels',
            csv_file_name="Ion channels - Ion Channel To Neuron.tsv",
            cell_type=Neuron.rdf_type,
            initial_cell_column=101)
    ctx(ConnectomeCSVDataSource)(
            key="emmons",
            csv_file_name="herm_full_edgelist.csv")
    ctx(WormBaseCSVDataSource)(
            key="wormbase_celegans_cells",
            csv_file_name="C. elegans Cell List - WormBase.csv",
            description="CSV converted from this Google Spreadsheet: "
            "https://docs.google.com/spreadsheets/d/"
            "1NDx9LRF_B2phR5w4HlEtxJzxx1ZIPT2gA0ZmNmozjos/edit#gid=1")
