import logging
L = logging.getLogger(__name__)


def merge_data_objects(a, b):
    if not (a.defined and b.defined and a.identifier() == b.identifier()):
        L.warning(
            repr(a) +
            " will not merge with " +
            repr(b) +
            " as it has the wrong identifier")
        return None
    else:
        eats = []
        for p in b.properties:
            q = getattr(a, p.linkName)
            if p.link != q.link:
                L.warning(
                    repr(q) +
                    " will not merge " +
                    repr(p) +
                    " as it has the wrong link")
                return None
            else:
                eats.append((q, p))

        for q, p in eats:
            q.eat(p)
        return a
