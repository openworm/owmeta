import neuroml as N
from owmeta_core.data import DataUser
from owmeta_core.dataobject import DataObject, DatatypeProperty
import owmeta_core.dataobject_property as DP
from rdflib.term import URIRef
from rdflib.namespace import Namespace

from . import CONTEXT, BASE_BIO_SCHEMA_URL

NEUROML_NS = Namespace(f'{BASE_BIO_SCHEMA_URL}/NeuroML#')


class NeuroMLDocument(DataObject):
    '''
    Represents a NeuroML document

    The document may be represented literally in the RDF graph using `xml_content` or
    stored elsewhere and included by reference with `document_url`.

    Example::

        >>> embedded_nml = NeuroMLDocument(key='embedded_ex', content="""\\
        ... <?xml version="1.0" encoding="UTF-8"?>
        ... <neuroml xmlns="http://www.neuroml.org/schema/neuroml2"
        ...     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        ...     xsi:schemaLocation="http://www.neuroml.org/schema/neuroml2
        ...     https://raw.github.com/NeuroML/NeuroML2/master/Schemas/NeuroML2/NeuroML_v2beta.xsd"
        ...     id="k_slow">
        ...     <ionChannel id="k_slow" conductance="10pS" type="ionChannelHH" species="k">
        ...         <notes>K slow channel from Boyle and Cohen 2008</notes>
        ...         <gateHHtauInf id="n" instances="1">
        ...             <timeCourse type="fixedTimeCourse" tau="25.0007 ms"/>
        ...             <steadyState type="HHSigmoidVariable" rate="1" scale="15.8512 mV" midpoint="19.8741 mV"/>
        ...         </gateHHtauInf>
        ...     </ionChannel>
        ... </neuroml>""")

        >>> external_nml = NeuroMLDocument(ident='external_ex',
        ...     document_url='')

    '''

    class_context = CONTEXT

    content = DatatypeProperty()
    '''
    XML content for the document. Should be a complete NeuroML document rather than a
    fragment.
    '''

    document_url = DatatypeProperty(multiple=True)
    '''
    URL where the XML content of the document can be retrieved
    '''


class NeuroMLProperty(DP.ObjectProperty):
    '''
    Property for attaching NeuroML documents to resources
    '''
    class_context = CONTEXT
    link = NEUROML_NS['neuroML']
    value_type = NeuroMLDocument
