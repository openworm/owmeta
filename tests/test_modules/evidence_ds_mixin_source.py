from owmeta_core.datasource import DataSource, Informational


class ASource(DataSource):
    class_context = 'http://example.org/a_context'
    a = Informational(display_name='A Value')
