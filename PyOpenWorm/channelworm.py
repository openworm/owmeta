from .experiment import Experiment
from .pProperty import Property
from .evidence import Evidence
from .dataObject import DataObject

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

    def __init__(self, reference=False, **kwargs):
        Experiment.__init__(self, reference)

        # enumerate conditions patch-clamp experiments should have
        self.conditions = [
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

        for c in self.conditions:
            PatchClampExperiment.DatatypeProperty(c, self)

        for c, v in kwargs.iteritems():
            if c in self.conditions:
                setattr(self, c, v)


class References(Property):
    multiple=True
    def __init__(self, **kwargs):
        Property.__init__(self, 'references', **kwargs)
        self._refs = []

    def set(self, e=False, **kwargs):
        """
        Add a reference to the list.
        This method will also take care of mapping the Evidence's assertion to
        this ChannelModel

        Parameters
        ----------
        e : Evidence or Experiment
            The Experiment or Evidence that supports this ChannelModel

        Returns
        -------
        None

        Example::

            e = P.Evidence(author='Sulston et al.', date='1983')
            cm = ChannelModel()
            cm.references.set(e)
        """
        if isinstance(e, Evidence):
            e.asserts(self.owner)
            self._refs.append(e)
        elif isinstance(e, Experiment):
            e = e.reference()
            e.asserts(self.owner)
            self._refs.append(e)

    def get(self, **kwargs):
        """
        Retrieve the reference list for this ChannelModel

        Parameters
        ----------
        None

        Returns
        -------
        Set of Evidence and Experiment objects
        """
        if len(self._refs) == 0:
            #Make dummy Evidence to load from db
            ev = Evidence()
            ev.asserts(self.owner)
            #Make dummy Experiment with this Evidence
            ex = Experiment(reference=ev)
            #load from db
            for e in ev.load():
                self._refs.append(e)
            for e in ex.load():
                self._refs.append(e)
        #now return the iterable set
        for r in self._refs:
            yield r

class ChannelModelType:
    patchClamp = "Patch clamp experiment"
    homologyEstimate = "Estimation based on homology"

class ChannelModel(DataObject):
    """
    A model for an ion channel.

    There may be multiple models for a single channel.

    Parameters
    ----------
    modelType : DatatypeProperty
        What this model is based on (either "homology" or "patch-clamp")

    Attributes
    ----------
    modelType : DatatypeProperty
        Passed in on construction
    ion : DatatypeProperty
        The type of ion this channel selects for
    gating : DatatypeProperty
        The gating mechanism for this channel ("voltage" or name of ligand(s) )
    references : Property
        Evidence for this model. May be either Experiment or Evidence object(s).
    conductance : DatatypeProperty
        The conductance of this ion channel. This is the initial value, and
        should be entered as a Quantity object.

    Example usage::

        # Create a ChannelModel
        >>> cm = P.ChannelModel()
        # Create Evidence object
        >>> ev = P.Evidence(author='White et al.', date='1986')
        # Assert
        >>> ev.asserts(cm)
        >>> ev.save()
    """

    def __init__(self, modelType=False, *args, **kwargs):
        DataObject.__init__(self, **kwargs)
        ChannelModel.DatatypeProperty('modelType', self)
        ChannelModel.DatatypeProperty('ion', self, multiple=True)
        ChannelModel.DatatypeProperty('gating', self, multiple=True)
        ChannelModel.DatatypeProperty('conductance', self)
        References(owner=self)

        #Change modelType value to something from ChannelModelType class on init
        if (isinstance(modelType, str)):
            modelType = modelType.lower()
            if modelType in ('homology', ChannelModelType.homologyEstimate):
                self.modelType(ChannelModelType.homologyEstimate)
            elif modelType in ('patch-clamp', ChannelModelType.patchClamp):
                self.modelType(ChannelModelType.patchClamp)

