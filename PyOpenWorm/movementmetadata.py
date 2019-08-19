from PyOpenWorm.context import Context
from PyOpenWorm.worm import Worm
from PyOpenWorm.dataObject import (DataObject,
                                   DatatypeProperty,
                                   ObjectProperty,
                                   Alias)


class Usage(DataObject):
    rights = DatatypeProperty()

class Provenance(DataObject):
    citation = DatatypeProperty()
    complementarydata = DatatypeProperty()
    processing = DatatypeProperty()
    previouspublications = DatatypeProperty()
    previewlink = DatatypeProperty()

class Collection(DataObject):
    lab_name = DatatypeProperty()
    lab_location = DatatypeProperty()
    collector = DatatypeProperty()
    timestamp = DatatypeProperty()
    humidity = DatatypeProperty()
    temperature = DatatypeProperty()
    arena_style = DatatypeProperty()
    arena_size = DatatypeProperty()
    arena_orientation = DatatypeProperty()
    food = DatatypeProperty()
    habituation = DatatypeProperty()
    media = DatatypeProperty()
    protocol = DatatypeProperty() #text description and keywords
    scope = DatatypeProperty()
    limitations = DatatypeProperty()
    interpolation = DatatypeProperty()


class BioDetails(DataObject):
    sex = DatatypeProperty()
    stage = DatatypeProperty()
    age = DatatypeProperty()
    strain = DatatypeProperty()
    strain_descr = DatatypeProperty()
    gene = DatatypeProperty()
    chromosome = DatatypeProperty()
    allele = DatatypeProperty()
    proteins = DatatypeProperty()
    daysofadulthood = DatatypeProperty()
    worm_id = DatatypeProperty()

class Software(DataObject):
    software_name = DatatypeProperty()
    software_version = DatatypeProperty()
    software_featureID = DatatypeProperty()
    featureID = DatatypeProperty()
    version = DatatypeProperty()
    settings = DatatypeProperty()
    time = DatatypeProperty()
    framespersecond = DatatypeProperty()
    mmperpixel = DatatypeProperty()
    nosegskel = DatatypeProperty()
    base_name = DatatypeProperty() #what is base_name - need to check this
    ventralside = DatatypeProperty()

class MovementMetadata(DataObject):
    usage = ObjectProperty(value_type=Usage)
    provenance = ObjectProperty(value_type=Provenance)
    collection = ObjectProperty(value_type=Collection)
    biodetails = ObjectProperty(value_type=BioDetails)
    software = ObjectProperty(value_type=Software)
    subject = ObjectProperty(value_type=Worm)




__yarom_mapped_classes__ = (MovementMetadata, Usage, Provenance, Collection, BioDetails, Software)
