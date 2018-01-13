from __future__ import absolute_import
from __future__ import print_function
import sys
from six.moves import zip
import unittest
import neuroml
import neuroml.writers as writers
import PyOpenWorm
import yarom
import os

from PyOpenWorm.data import DataUser
from .DataTestTemplate import _DataTest

from PyOpenWorm.neuron import Neuron
from PyOpenWorm.muscle import Muscle
from PyOpenWorm.cell import Cell


class CellTest(_DataTest):
    ctx_classes = (Cell, Neuron, Muscle)

    def test_DataUser(self):
        do = Cell('', conf=self.config)
        self.assertTrue(isinstance(do, DataUser))

    def test_lineageName(self):
        """ Test that we can retrieve the lineage name """
        c = self.ctx.Cell(name="ADAL", conf=self.config)
        c.lineageName("AB plapaaaapp")
        self.save()
        self.assertEqual("AB plapaaaapp", Cell(name="ADAL").lineageName())

    def test_wormbaseID(self):
        """ Test that a Cell object has a wormbase ID """
        c = self.ctx.Cell(name="ADAL", conf=self.config)
        c.wormbaseID("WBbt:0004013")
        self.save()
        self.assertEqual("WBbt:0004013", self.ctx.Cell(name="ADAL").wormbaseID())

    def test_synonyms(self):
        """ Test that we can add and retrieve synonyms. """
        c = self.ctx.Cell(name="ADAL", conf=self.config)
        c.synonym("lineage name: ABplapaaaapp")
        self.save()
        self.assertEqual(
            set(["lineage name: ABplapaaaapp"]),
            self.ctx.Cell(name="ADAL").synonym())

    def test_same_name_same_id(self):
        """
        Test that two Cell objects with the same name have the same
        identifier

        Saves us from having too many inserts of the same object.
        """
        c = Cell(name="boots")
        c1 = Cell(name="boots")
        self.assertEqual(c.identifier, c1.identifier)

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
        p = self.ctx.Cell(name="peas")
        base = 'ab.tahsuetoahusenoat'
        p.lineageName(base)
        self.save()

        c = ["carrots",
             "jam",
             "peanuts",
             "celery",
             "tuna",
             "chicken"]

        division_directions = "alvpdr"

        for x, l in zip(c, division_directions):
            ln = base + l
            self.ctx.Cell(name=x, lineageName=ln)
        self.save()
        names = set(str(x.name()) for x in p.parentOf())
        self.assertEqual(set(c), names)

    def test_daughterOf(self):
        """
        Test that we can get the parent of a cell
        """
        base = "ab.tahsuetoahusenoat"
        child = base + "u"
        p = self.ctx.Cell(name="peas")
        p.lineageName(base)
        self.save()
        c = self.ctx.Cell(name="carrots")
        c.lineageName(child)
        self.save()
        parent_p = c.daughterOf().name()
        self.assertEqual("peas", parent_p)

    @unittest.skip('Long runner')
    def test_morphology_is_NeuroML_morphology(self):
        """ Check that the morphology is the kind made by neuroml """
        c = Cell(name="ADAR", conf=self.config)
        # get the morph
        m = c.morphology()
        self.assertIsInstance(m, neuroml.Morphology)

    @unittest.skip('Long runner')
    def test_morphology_validates(self):
        """ Check that we can generate a cell's file and have it validate """
        # Load in raw morphology for ADAL
        self.config['rdf.graph'].parse(
            "tests/test_data/PVDR.nml.rdf.xml",
            format='trig')
        n = Neuron(name='PVDR', conf=self.config)
        doc = PyOpenWorm.NeuroML.generate(n, 1)
        writers.NeuroMLWriter.write(doc, "temp.nml")
        from neuroml.utils import validate_neuroml2
        f = sys.stdout
        try:
            sys.stdout = open(os.devnull, 'w')
        except Exception:
            sys.stdout = f

        try:
            validate_neuroml2("temp.nml")
        except Exception:
            self.fail("Should validate")
        sys.stdout = f

    def test_loading_cells_retrieves_all_cells(self):
        """
        Test that retrieving all Cells gives us the right number of Cell
        objects.
        """
        num_cells = len(list(Cell().load()))

        m = list(Muscle().load())
        num_muscles = len(m)

        n = list(Neuron().load())
        num_neurons = len(n)

        sum_cells = num_neurons + num_muscles

        self.assertEqual(sum_cells, num_cells)

    def test_str(self):
        self.assertEqual('cell_name', str(Cell('cell_name')))
