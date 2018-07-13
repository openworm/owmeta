from yarom.utils import slice_dict

from .experiment import Experiment
from .dataObject import DataObject, DatatypeProperty, ObjectProperty
from .channel_common import CHANNEL_RDF_TYPE
from . import SCI_BIO_CTX


class PatchClampExperiment(Experiment):
    """
    Store experimental conditions for a patch clamp experiment.

    Attributes
    ----------
    Ca_concentration : DatatypeProperty
        Calcium concentration
    Cl_concentration : DatatypeProperty
        Chlorine concentration
    blockers : DatatypeProperty
        Channel blockers used for this experiment
    cell : DatatypeProperty
        The cell this experiment was performed on
    cell_age : DatatypeProperty
        Age of the cell
    delta_t : DatatypeProperty

    duration : DatatypeProperty

    end_time : DatatypeProperty

    extra_solution : DatatypeProperty

    initial_voltage : DatatypeProperty
        Starting voltage of the patch clamp
    ion_channel : DatatypeProperty
        The ion channel being clamped
    membrane_capacitance : DatatypeProperty
        Initial membrane capacitance
    mutants : DatatypeProperty
        Type(s) of mutants being used in this experiment
    patch_type : DatatypeProperty
        Type of patch clamp being used ('voltage' or 'current')
    pipette_solution : DatatypeProperty
        Type of solution in the pipette
    protocol_end : DatatypeProperty

    protocol_start : DatatypeProperty

    protocol_step : DatatypeProperty

    start_time : DatatypeProperty

    temperature : DatatypeProperty

    type : DatatypeProperty

    """
    class_context = SCI_BIO_CTX.identifier

    conditions = [
        'Ca_concentration',
        'Cl_concentration',
        'blockers',
        'cell',
        'cell_age',
        'delta_t',
        'duration',
        'end_time',
        'extra_solution',
        'initial_voltage',
        'ion_channel',
        'membrane_capacitance',
        'mutants',
        'patch_type',
        'pipette_solution',
        'protocol_end',
        'protocol_start',
        'protocol_step',
        'start_time',
        'temperature',
        'type',
    ]

    def __init__(self, reference=False, **kwargs):
        conditions = slice_dict(kwargs, self.conditions)
        kwargs = {k: kwargs[k] for k in kwargs if k not in conditions}
        super(PatchClampExperiment, self).__init__(reference, **kwargs)

        # enumerate conditions patch-clamp experiments should have

        for c in self.conditions:
            PatchClampExperiment.DatatypeProperty(c, self)

        for c, v in conditions.items():
            getattr(self, c).set(v)


class ChannelModelType:
    patchClamp = "Patch clamp experiment"
    homologyEstimate = "Estimation based on homology"


class ChannelModel(DataObject):
    """
    A model for an ion channel.

    There may be multiple models for a single channel.

    Example usage::

        # Create a ChannelModel
        >>> cm = P.ChannelModel()
        # Create Evidence object
        >>> ev = P.Evidence(author='White et al.', date='1986')
        # Assert
        >>> ev.asserts(cm)
        >>> ev.save()
    """
    class_context = SCI_BIO_CTX.identifier

    modelType = DatatypeProperty()
    ''' The type of model employed to describe a channel '''

    ion = DatatypeProperty(multiple=True)
    ''' The type of ion this channel selects for '''

    gating = DatatypeProperty(multiple=True)
    ''' The gating mechanism for this channel ("voltage" or name of ligand(s) ) '''

    conductance = DatatypeProperty()
    ''' The conductance of this ion channel. This is the initial value, and should be entered as a Quantity object. '''

    def __init__(self, modelType=None, *args, **kwargs):
        super(ChannelModel, self).__init__(*args, **kwargs)

        #Change modelType value to something from ChannelModelType class on init
        if isinstance(modelType, str):
            modelType = modelType.lower()
            if modelType in ('homology', ChannelModelType.homologyEstimate):
                self.modelType(ChannelModelType.homologyEstimate)
            elif modelType in ('patch-clamp', ChannelModelType.patchClamp):
                self.modelType(ChannelModelType.patchClamp)


class PatchClampChannelModel(ChannelModel):
    modeled_from = ObjectProperty(value_type=PatchClampExperiment)

    def __init__(self, **kwargs):
        super(PatchClampChannelModel, self).__init__(modelType='patch-clamp',
                                                     **kwargs)


class HomologyChannelModel(ChannelModel):
    homolog = ObjectProperty(value_rdf_type=CHANNEL_RDF_TYPE)

    def __init__(self, **kwargs):
        super(HomologyChannelModel, self).__init__(modelType='homology',
                                                   **kwargs)


__yarom_mapped_classes__ = (ChannelModel, HomologyChannelModel, PatchClampChannelModel, PatchClampExperiment)
