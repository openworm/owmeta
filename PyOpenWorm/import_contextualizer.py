
class ImportContextualizer(object):
    """ Interface for classes that 'contextualize' an import.

    Contextualizing an import means that if an object is defined with the name
    X in some context, and an import statement is written like this::

        import X.a

    X will be invoked like this::

        a = X(__import__('a'))

    On the other hand, for an import statement of this form::

        from X.a import A

    will cause X to be invoked as::

        _temp = X(__import__('a', globals(), locals(), ('A',)), ('A',))
        A = _temp.A

    and the import statement::

        from X.a import A as AA

    will cause X to be invoked as::

        _temp = X(__import__('a', globals(), locals(), ('A',)), ('A',))
        AA = _temp.A

    meaning that the contextualizer won't know what the 'as' name is.

    For the astute reader, you may notice parallels between the protocol for
    ImportContextualizer and the __import__ function itself. You may also be
    wondering why the contextualizer isn't merely a proxy for __import__. The
    first reason is that I want the true import to always happen, regardless of
    what the contextualizer does, so that the semantics of the contextualizer
    are very clear. The second reason is that requiring a real proxy would
    require more complexity in the contextualizers to ensure that they are
    properly handling exceptions, module attributes and the return value of
    __import__, ensuring that the *right* __import__ is used, as well as
    handling the 'fromlist' correctly.
    """
    def __call__(self, module):
        raise NotImplementedError()
