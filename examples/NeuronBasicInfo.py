"""
Get information about a neuron from the database.
In this case we are getting a list of neurons associated with each neuron type.

Note how the attributes of a neuron are accessed: `list(neuron.attribute())`
where attribute is one of the attributes outlined in the neuron API.

Also note that, for attributes with only one value, the value can be accessed by
doing `neuron.attribute.one()`.

Example: Something like `adal.name.one()` might return "ADAL", assuming we have
declared the variable `adal`.
"""

from __future__ import print_function
import PyOpenWorm as P
import os
print(os.getcwd())
P.connect()
def get_names(it):
    res = []
    for x in it:
        res.append(x.name())
    return res

w = P.Worm()
net = w.neuron_network()
print("Retrieving names...")
inter = get_names(net.interneurons())
motor = get_names(net.motor())
sensory = get_names(net.sensory())

print("Calculating combinations...")
sensmot = set(sensory) & set(motor)
sensint = set(sensory) & set(inter)
motint = set(motor) & set(inter)
sens_only = set(sensory) - set(motor) - set(inter)
motor_only = set(motor) - set(sensory) - set(inter)
inter_only = set(inter) - set(sensory) - set(motor)
tri = motint & set(sensory)
motint_no_tri = motint - tri
sensint_no_tri = sensint - tri
sensmot_no_tri = sensmot - tri
def pp_set(title, s):
    print(title)
    print("="*(len(title)))
    print(" ".join(s))
    print()

pp_set("Sensory only neurons",sens_only)
pp_set("Interneurons (not mechanosensory, etc.)",inter_only)
pp_set("Motor only neurons",motor_only)
pp_set("Sensory-motor neurons",sensmot)
pp_set("Sensory and interneuron?",sensint)
pp_set("Motor and interneuron?",motint)
pp_set("Sensory-motor less tri-functional",sensmot_no_tri)
pp_set("Motor and interneuron less tri-functional",motint_no_tri)
pp_set("Sensory and interneuron less tri-functional",sensint_no_tri)
