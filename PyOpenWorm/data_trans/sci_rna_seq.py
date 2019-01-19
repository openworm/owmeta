from rpy2.robjects.packages import importr
from rpy2.robjects import r as R
from PyOpenWorm.datasource import DataTranslator, DataSource, Informational


class SCIRNASeqDataSource(DataSource):
    data_url = Informational('Data URL')


class SCIRNASeqTranslator(DataTranslator):

    def translate(self, ds):
        url = ds.data_url().pop()
        base = importr('base')
        utils = importr('utils')
        utils.download_file(url, destfile="data_source.RData")
        base.load("data_source.RData")
        cds = R('cds')
        print(cds)


__yarom_mapped_classes__ = (SCIRNASeqTranslator, SCIRNASeqDataSource)
