import sys
sys.path.insert(0,'..')
import PyOpenWorm as P
P.connect(testConfig=True)
n = P.Neuron(name='AVAL')
# insert some connections
#n1 = Neuron("DA3")
#c = Connection(pre=n,post=n1,synclass="send")
for x in n.connection():
    print x
