"""
Demo:
"""

import sys
sys.path.insert(0,'..')
import PyOpenWorm as P

#Create dummy database configuration.
d = P.Data({
    "rdf.upload_block_statement_count" : 50,
    "user.email" : "jerry@cn.com"
})

P.connect(conf=d)
n = P.Neuron(name='AVAL')
# insert some connections
n1 = P.Neuron("DA3")
c = P.Connection(pre_cell=n, post_cell=n1, syntype="send")

n.connection.set(c)

print n.connection.get(pre_post_or_either='either')

print n.conns

for x in n.connection:
    print x
