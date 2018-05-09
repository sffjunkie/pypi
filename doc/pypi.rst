pypi: server, protocol, module and tool
=======================================

Under the `pypi` umbrella we could (and possibly should) provide 4 elements

`The Server`_ - pypi-server
	The web front end, middleware and backend to the distributions stored
	in the repository.

`The Protocol`_ - pypi-protocol
	A formal written definition of how to talk to the server middleware to
	search/upload/download distributions etc.

`The Module`_ - pypi
	A Python client module to interact with pypi backend using the protocol.

`The Tool`_ - pypi-cli
	A command line application to search/upload/download distributions

.. _The Server:

The Server
~~~~~~~~~~

Provides a Frontend
	Allows a human to browse the index, search for packages from a friendly
	web based interface.

Middleware
	The pypi protocol support for interfacing with `The Module`_ / `The Tool`_.

and a Backend
	Validates uploaded distributions and stores their info in the database

* The currently deployed version of PyPi is codename ``pypi`` available at https://pypi.org

* The next version is codename ``warehouse`` available at https://warehouse.pypi.org

* A package index for the purposes testing of testing interaction with PyPi is also
  provided https://test.pypi.org.

.. _The Protocol:

The Protocol
~~~~~~~~~~~~

Defines the communications between The Server Middleware and The Module.

Uses the :ref:`jsonrpc` protocol.

Legacy tools talk to the Middleware using the :ref:`xmlrpc` protocol.

.. _The Module:

The Module
~~~~~~~~~~

* Provides a default implementation of the protocol.
* Allows other projects to provide an interface to a repositiory.
* This would extract various bits of functionality fromm `pip` and `twine`.
* Uses the User Agent format used by Pip

.. _The Tool:

The Tool
~~~~~~~~

A frontend to the module that allows the user to interact with pypi via the command line.

The following functionality should be provided...

	* search for projects
	* get info about a project (list of distributions) or a specific distribution
	* download a distribution; sdist, wheel
	* login
	* add a project
	* upload a distribution; sdist or wheel
	* upload metadata (possibly)

* Initially will only work with ``sdist``\s and ``bdist_wheel`` format distribution packages
* Possibly expand distribution formats to include stubs, docs, tests
* Signing, like twine, is to be handled by external tools.


Commands
--------

* search
	- \*args = search in name and summary fields
	- \*\*kwargs = search in named fields
* download distribution
* download distribution from requirements
* login - only runs in an interactive session
* create project
* upload metadata
* upload distribution
* status of a distribution
* create cache
* upload docs

Environment Variables
---------------------

* PYPI_REPOSITORY - Repository Name (pypi, warehouse, test_pypi) or URL
* PYPI_USERNAME
* PYPI_PASSWORD
* PYPI_CA_BUNDLE - A CA bundle

Package Indexes
~~~~~~~~~~~~~~~

* PyPi = PackageIndex('https://pypi.org/')
* Warehouse = PackageIndex('https://warehouse.pypi.org/')
* TestPyPi = PackageIndex('https://test.pypi.org/')
* LegacyPyPi = PackageIndex('https://pypi.python.org/pypi/')

Misc
~~~~

* Should only use https

.. _pypi: https://pypi.org
.. _warehouse: https://warehouse.pypi.org
.. _test_pypi: https://test.pypi.org
