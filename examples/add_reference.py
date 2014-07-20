import sys
sys.path.insert(0,'..')
import PyOpenWorm as P

d = P.Data({
    "rdf.upload_block_statement_count" : 50,
    "user.email" : "jerry@cn.com"
})
logging = False
if len(sys.argv) > 1 and sys.argv[1] == '-l':
    logging = True
P.connect(conf=d,do_logging=logging)
n = P.Neuron(name='AVAL')
#n.receptor('GGR-3')
#n.receptor('GLR-5')
e = P.Evidence(doi='125.41.3/ploscompbiol', pmid = '57182010')
e.asserts(n.receptor('UNC-8'))
n.save()
e.save()
e1 = P.Evidence()
e1.asserts(n.receptor)
for p in e1.load():
    print p
P.disconnect()
