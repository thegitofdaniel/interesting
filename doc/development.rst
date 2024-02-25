Development
===========

Run tests
---------

.. code-block:: python

    python -m pytest

Run test coverage
-----------------

.. code-block:: bash

    # run tests
    coverage run -m pytest

    # print brief report
    coverage report -m

    # generate html report
    coverage html

    # open report in browser
    cd htmlcov
    open index.html

Pre-Commit (Format and Linting)
--------------------------------

.. code-block:: bash

    # pre-commit (ruff + other hooks)
    pre-commit run -a

    # just ruff: check
    ruff check .

    # just ruff: check and fix
    ruff check . --fix
