'''
This example uses the WCON JSON-schema to build a DataSource type and then creates a new
DataSource with the values from an instance conforming to the schema
'''
from os.path import join as p, dirname
import json

from PyOpenWorm.json_schema import Creator, DataSourceTypeCreator
from PyOpenWorm.context import Context, ClassContext


with open(p(dirname(__file__), 'wcon_schema.json'), 'r') as f:
    schema = json.load(f)

data_path = p(dirname(__file__), 'noflpp.json')
# data_path = p(dirname(__file__), 'N2 on food L_2010_05_18__12_16_13___7___2.wcon')
with open(data_path, 'r') as f:
    data = json.load(f)

# The context of the DataSourceTypeCreator determines the definition context for the
# classes created *unless* the schema definitions have an "$id", in which case the value
# of the "$id" field takes precedence
def_ctx = ClassContext(ident='http://openworm.org/tracker-commons')
annotated_schema = DataSourceTypeCreator('WCONDataSource', schema, context=def_ctx).annotate()

# The context of the Creator determines the context in which statements are made by the
# creator
stmt_ctx = Context(ident='http://example.org/json_schema/example')
ob = Creator(annotated_schema).create(data, context=stmt_ctx, ident="http://example.org/wcon_data_source")

print(stmt_ctx.staged.rdf_graph().serialize(format='n3').decode('utf-8'))
