from PyOpenWorm.neuron import Neuron

from PyOpenWorm.data import DataUser
import neuroml as N


class NeuroML(DataUser):
    @classmethod
    def generate(cls, o, t=2):
        """
        Get a NeuroML object that represents the given object. The ``type``
        determines what content is included in the NeuroML object:

        :param o: The object to generate neuroml from
        :param t: The what kind of content should be included in the document
                    - 0=full morphology+biophysics
                    - 1=cell body only+biophysics
                    - 2=full morphology only
        :returns: A NeuroML object that represents the given object.
        :rtype: NeuroMLDocument
        """
        if isinstance(o, Neuron):
            # read in the morphology data
            d = N.NeuroMLDocument(id=o.name())
            c = N.Cell(id=o.name())
            c.morphology = o.morphology()
            d.cells.append(c)
            return d
        else:
            raise "Not a valid object for conversion to neuroml"

    @classmethod
    def write(cls, o, n):
        """
        Write the given neuroml document object out to a file
        :param o: The NeuroMLDocument to write
        :param n: The name of the file to write to
        """
        N.writers.NeuroMLWriter.write(o, n)

    @classmethod
    def validate(cls, o):
        pass
