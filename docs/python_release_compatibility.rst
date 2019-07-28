.. _python_release_compatibility:

Python Release Compatibility
============================
All Python releases will be supported until they reach their official
end-of-life, typically reported as "Release Schedule" PEPs (search "release
schedule" on the `PEP index <https://www.python.org/dev/peps/#id7>`_)
Thereafter, any regressions due to dependencies of |pow| dropping support for
an EOL Python version, or due to a change in |pow| making use of a feature in a
still-supported Python release will only be fixed for the sake of OpenWorm
projects when requested by an issue on `our tracker
<https://github.com/openworm/PyOpenWorm/issues>`_ or for other projects when a
compelling case can be made.

This policy is intended to provide support to most well-maintained projects
which depend on |pow| while not overburdening developers.
