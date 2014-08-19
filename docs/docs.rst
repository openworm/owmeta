.. _docs:

Adding documentation
---------------------
Documentation for |pow| is housed in two locations: 

    #. In the top-level project directory as :file:`INSTALL.md` and :file:`README.md`. 
    #. Under the ``docs`` directory

To add a page about useful facts concerning C. elegans to the documentation, include an entry in the list under ``toctree`` in :file:`docs/index.rst` like::

    worm-facts

and create the file :file:`worm-facts.rst` under the :file:`docs` directory and add a line::

    .. _worm-facts:

to the top of your file, remembering to leave an empty line before adding all of your wonderful worm facts.

You can get a preview of what your documentation will look like when it is published by running ``sphinx-build`` on the docs directory::

    sphinx-build -w sphinx-errors docs build_destination

The docs will be compiled to html which you can view by pointing your web browser at :file:`build_destination/index.html`. If you want to view the documentation locally with the `ReadTheDocs theme <https://github.com/snide/sphinx_rtd_theme>`_ you'll need to download and install it.

Currently there are no real conventions to follow for documentation style, but additions will be subject to review by project maintainers. 
