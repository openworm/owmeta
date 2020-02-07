from __future__ import print_function, absolute_import

import logging

from owmeta_core.command_util import GenericUserError
from owmeta_core.dataobject import DataObject

from .commands.biology import CellCmd


L = logging.getLogger(__name__)


class OWMEvidence(object):
    '''
    Commands for evidence
    '''
    def __init__(self, parent):
        self._parent = parent

    def get(self, identifier, rdf_type=None):
        '''
        Retrieves evidence for the given object. If there are multiple types for the object, the evidence for only one
        type will be shown, but you can specify which type should be used.

        Parameters
        ----------
        identifier : str
            The object to show evidence for
        rdf_type : str
            Type of the object to show evidence
        '''
        from owmeta.evidence import Evidence
        from owmeta.data_trans.data_with_evidence_ds import DataWithEvidenceDataSource
        from owmeta_core.context_dataobject import ContextDataObject
        ctx = self._parent._default_ctx.stored
        identifier = self._parent._den3(identifier)
        rdf_type = self._parent._den3(rdf_type)
        if rdf_type:
            base_type = ctx(ctx.resolve_class(rdf_type))
            if base_type is None:
                raise GenericUserError("Could not find Python class corresponding to " +
                        str(rdf_type))
        else:
            base_type = ctx(DataObject)

        q = base_type.query(ident=identifier)
        for l in q.load():
            if isinstance(l, ContextDataObject):
                evq = ctx(Evidence).query()
                evq.supports(l)
                self._message_evidence(evq)
            if isinstance(l, DataWithEvidenceDataSource):
                evq = l.evidence_context.stored(Evidence).query()
                self._message_evidence(evq)

    def _message_evidence(self, evq):
        from owmeta.website import Website
        from owmeta.document import Document
        msg = self._parent.message
        for m in evq.load():
            ref = m.reference()
            if isinstance(ref, Document):
                msg(ref)
                titles = ['Author:',
                          'Title: ',
                          'URI:   ',
                          'DOI:   ',
                          'PMID:  ',
                          'WBID:  ']
                vals = [ref.author(),
                        ref.title(),
                        ref.uri(),
                        ref.doi(),
                        ref.pmid(),
                        ref.wbid()]
                for title, v in zip(titles, vals):
                    if v:
                        msg(title, v)
                msg()
            elif isinstance(ref, Website):
                msg(ref)
                titles = ['Title: ',
                          'URL:   ']
                vals = [ref.title(),
                        ref.url()]
                for title, v in zip(titles, vals):
                    if v:
                        msg(title, v)
                msg()
