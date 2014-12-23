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

import PyOpenWorm as P

#Connect to the database.
P.connect("default.conf")

#Get the worm object.
worm = P.Worm()

#Extract the network object from the worm.
net = worm.get_neuron_network()

#Declare an empty dictionary.
types = {}

#Go through the neuron objects in the network.
for neuron in net.neuron():
    if len(list(neuron.type())) > 0:
        #i.e. "If there is a type associated with a neuron:"
        type = list(neuron.type())[0]

        if not types.has_key(type):
            #If this type key is not already in our dictionary, add it.
            types[type] = []

        #Add the neuron's name under its type key in our dictionary.
        types[type].append(list(neuron.name())[0])

for type in types.keys():
    #Print out the types of neurons and list the associated neurons with each.
    print("Neurons of type %s:\n  %s\n"%(type, types[type]))
