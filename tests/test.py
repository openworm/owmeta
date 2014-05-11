# -*- coding: utf-8 -*-

import unittest

import PyOpenWorm
from PyOpenWorm import Configure,Network,Worm,Neuron,Data
import networkx
import rdflib


class PyOpenWormTest(unittest.TestCase):
    """Test for PyOpenWorm."""

    @classmethod
    def setUpClass(cls):
        c = Configure()
        c['connectomecsv'] = 'https://raw.github.com/openworm/data-viz/master/HivePlots/connectome.csv'
        c['neuronscsv'] = 'https://raw.github.com/openworm/data-viz/master/HivePlots/neurons.csv'
        c['sqldb'] = '/home/markw/work/openworm/PyOpenWorm/db/celegans.db'
        c = Data(c)
        cls.config = c
        cls.net = Network(c)

    def test_network(self):
        self.assertTrue(isinstance(self.net,Network))

    def test_network_aneuron(self):
    	  self.assertTrue(isinstance(self.net.aneuron('AVAL'),PyOpenWorm.Neuron))

    def test_network_neurons(self):
   	  self.assertTrue('AVAL' in self.net.neurons())
   	  self.assertTrue('DD5' in self.net.neurons())
   	  self.assertEquals(len(self.net.neurons()), 302)

    def test_worm_muscles(self):
   	  self.assertTrue('MDL08' in PyOpenWorm.Worm(self.config).muscles())
   	  self.assertTrue('MDL15' in PyOpenWorm.Worm(self.config).muscles())

    def test_neuron_type(self):
    	  self.assertEquals(self.net.aneuron('AVAL').type(),'interneuron')
    	  self.assertEquals(self.net.aneuron('DD5').type(),'motor')
    	  self.assertEquals(self.net.aneuron('PHAL').type(),'sensory')

    def test_neuron_name(self):
    	  self.assertEquals(self.net.aneuron('AVAL').name(),'AVAL')
    	  self.assertEquals(self.net.aneuron('AVAR').name(),'AVAR')

    def test_neuron_GJ_degree(self):
    	  self.assertEquals(self.net.aneuron('AVAL').GJ_degree(),60)

    def test_neuron_Syn_degree(self):
    	  self.assertEquals(self.net.aneuron('AVAL').Syn_degree(),74)

    def test_network_as_networkx(self):
    	  self.assertTrue(isinstance(self.net.as_networkx(),networkx.DiGraph))

    def test_neuron_receptors(self):
	  self.assertTrue('GLR-2' in Neuron('AVAL',self.config).receptors())
	  self.assertTrue('OSM-9' in Neuron('PHAL',self.config).receptors())

    def test_worm_get_network(self):
        self.assertTrue(isinstance(PyOpenWorm.Worm(self.config).get_neuron_network(), PyOpenWorm.Network))

    def test_worm_get_semantic_net(self):
        g0 = PyOpenWorm.Worm(self.config).get_semantic_net()
        self.assertTrue(isinstance(g0, rdflib.ConjunctiveGraph))

        qres = g0.query(
            """
            SELECT ?subLabel     #we want to get out the labels associated with the objects
            WHERE {
              GRAPH ?g { #Each triple is in its own sub-graph to enable provenance
                # match all subjects that have the 'is a' (1515) property pointing to 'muscle' (1519)
                ?subject <http://openworm.org/entities/1515> <http://openworm.org/entities/1519> .
                }
              #Triples that have the label are in the main graph only
              ?subject rdfs:label ?subLabel  #for the subject, look up their plain text label.
            }
            """)
        list = []
        for r in qres.result:
            list.append(str(r[0]))
        self.assertTrue('MDL08' in list)

    def test_neuron_get_reference(self):
        self.assertIn('http://dx.doi.org/10.100.123/natneuro', PyOpenWorm.Neuron('ADER',self.config).get_reference(0,'EXP-1'))
        self.assertEquals(PyOpenWorm.Neuron('ADER',self.config).get_reference(0,'DOP-2'), [])

    def test_neuron_add_reference(self):
        PyOpenWorm.Neuron('ADER', self.config).add_reference('receptor', 'EXP-1', pmid='some_pmid')
        self.assertIn('some_pmid', PyOpenWorm.Neuron('ADER',self.config).get_reference(0,'EXP-1'))
        self.config._properties['semantic_net'].invalidate()

    def test_muscle(self):
        self.assertTrue(isinstance(PyOpenWorm.Muscle('MDL08'),PyOpenWorm.Muscle))

    def test_configure_literal(self):
        c = Configure()
        c['seven'] = "coke"
        self.assertEquals(c['seven'], "coke")

    def test_configure_getter(self):
        c = Configure()
        class pipe:
            def get(self):
                return "sign"
        c['seven'] = pipe()
        self.assertEquals(c['seven'], "sign")

    def test_configure_late_get(self):
        c = Configure()
        a = {'t' : False}
        class pipe:
            def get(self):
                a['t'] = True
                return "sign"
        c['seven'] = pipe()
        self.assertFalse(a['t'])
        self.assertEquals(c['seven'], "sign")
        self.assertTrue(a['t'])

    def test_muscle_neurons(self):
        m = PyOpenWorm.Muscle('MDL08',self.config).neurons()
        for k in m:
            print k

