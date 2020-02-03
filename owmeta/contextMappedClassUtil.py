from rdflib.term import URIRef
import six

from .context import ClassContext


def find_class_context(dct, bases):
    ctx = None
    ctx_or_ctx_uri = dct.get('class_context', None)
    if ctx_or_ctx_uri is None:
        for b in bases:
            pctx = getattr(b, 'definition_context', None)
            if pctx is not None:
                ctx = pctx
                break
    else:
        if not isinstance(ctx_or_ctx_uri, URIRef) \
           and isinstance(ctx_or_ctx_uri, (str, six.text_type)):
            ctx_or_ctx_uri = URIRef(ctx_or_ctx_uri)
        if isinstance(ctx_or_ctx_uri, (str, six.text_type)):
            ctx = ClassContext(ctx_or_ctx_uri)
        else:
            ctx = ctx_or_ctx_uri
    return ctx


def find_base_namespace(dct, bases):
    base_ns = dct.get('base_namespace', None)
    if base_ns is None:
        for b in bases:
            if hasattr(b, 'base_namespace') and b.base_namespace is not None:
                base_ns = b.base_namespace
                break
    return base_ns
