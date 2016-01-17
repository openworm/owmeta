import sys
sys.path.insert(0,".")
import unittest
import neuroml
import neuroml.writers as writers
import PyOpenWorm
from PyOpenWorm import *
import networkx
import rdflib
import rdflib as R
import pint as Q
import os
import subprocess as SP
import subprocess
import tempfile
import doctest

from glob import glob

from GraphDBInit import *

from DataTestTemplate import _DataTest

class CellTest(_DataTest):

    def test_DataUser(self):
        do = Cell('',conf=self.config)
        self.assertTrue(isinstance(do,DataUser))

    def test_lineageName(self):
        """ Test that we can retrieve the lineage name """
        c = Cell(name="ADAL",conf=self.config)
        c.lineageName("AB plapaaaapp")
        c.save()
        self.assertEqual("AB plapaaaapp", Cell(name="ADAL").lineageName())

    def test_wormbaseID(self):
        """ Test that a Cell object has a wormbase ID """
        c = Cell(name="ADAL",conf=self.config)
        c.wormbaseID("WBbt:0004013")
        c.save()
        self.assertEqual("WBbt:0004013", Cell(name="ADAL").wormbaseID())

    def test_synonyms(self):
        """ Test that we can add and retrieve synonyms. """
        c = Cell(name="ADAL",conf=self.config)
        c.synonym("lineage name: ABplapaaaapp")
        c.save()
        self.assertEqual(set(["lineage name: ABplapaaaapp"]), Cell(name="ADAL").synonym())

    def test_same_name_same_id(self):
        """
        Test that two Cell objects with the same name have the same identifier()
        Saves us from having too many inserts of the same object.
        """
        c = Cell(name="boots")
        c1 = Cell(name="boots")
        self.assertEqual(c.identifier(),c1.identifier())

    def test_blast_space(self):
        """
        Test that setting the lineage name gives the blast cell.
        """
        c = Cell(name="carrots")
        c.lineageName("a tahsuetoahusenoatu")
        self.assertEqual(c.blast(), "a")

    def test_blast_dot(self):
        """
        Test that setting the lineage name gives the blast cell.
        """
        c = Cell(name="peas")
        c.lineageName("ab.tahsuetoahusenoatu")
        self.assertEqual(c.blast(), "ab")

    def test_parentOf(self):
        """
        Test that we can get the children of a cell
        Tests for anterior, posterior, left, right, ventral, dorsal divisions
        """
        p = Cell(name="peas")
        base = 'ab.tahsuetoahusenoat'
        p.lineageName(base)
        p.save()

        c = ["carrots",
             "jam",
             "peanuts",
             "celery",
             "tuna",
             "chicken"]

        division_directions = "alvpdr"

        for x,l in zip(c, division_directions):
            ln = base + l
            Cell(name=x,lineageName=ln).save()
        names = set(str(x.name()) for x in p.parentOf())
        self.assertEqual(set(c), names)

    def test_daughterOf(self):
        """
        Test that we can get the parent of a cell
        """
        base = "ab.tahsuetoahusenoat"
        child = base + "u"
        p = Cell(name="peas")
        p.lineageName(base)
        p.save()
        c = Cell(name="carrots")
        c.lineageName(child)
        c.save()
        parent_p = c.daughterOf().name()
        self.assertEqual("peas", parent_p)

    @unittest.skip('Long runner')
    def test_morphology_is_NeuroML_morphology(self):
        """ Check that the morphology is the kind made by neuroml """
        c = Cell(name="ADAR",conf=self.config)
        # get the morph
        m = c.morphology()
        self.assertIsInstance(m, neuroml.Morphology)

    @unittest.skip('Long runner')
    def test_morphology_validates(self):
        """ Check that we can generate a cell's file and have it validate """
        # Load in raw morphology for ADAL
        self.config['rdf.graph'].parse("tests/test_data/PVDR.nml.rdf.xml",format='trig')
        n = Neuron(name='PVDR', conf=self.config)
        doc = PyOpenWorm.NeuroML.generate(n,1)
        writers.NeuroMLWriter.write(doc, "temp.nml")
        from neuroml.utils import validate_neuroml2
        f = sys.stdout
        try:
            sys.stdout = open(os.devnull, 'w')
        except:
            sys.stdout = f

        try:
            validate_neuroml2("temp.nml")
        except Exception, e:
            print e
            self.fail("Should validate")
        sys.stdout = f

    def test_loading_cells_retrieves_all_cells(self):
        """
        Test that retrieving all Cells gives us the right number of Cell objects.
        """
        num_cells = len(list(Cell().load()))

        m = list(Muscle().load())
        num_muscles = len(m)

        n = list(Neuron().load())
        num_neurons = len(n)

        sum_cells = num_neurons + num_muscles

        self.assertEqual(sum_cells, num_cells)
