Packaging
=========

This project uses PDM to package and publish code.

Virtual Environment
-----

Create a virtual environment (if needed).

.. code-block:: bash

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Setup
-----

A PDM project needs to be initialized before it may be built (packaged) and published.

.. code-block:: bash

    pip install pdm

    pdm init

    pdm build

Install locally
---------------

With pip:

.. code-block:: bash

    pip install -e .

With pdm:

.. code-block:: bash

    pdm install -e .

Publising
---------

The publishing of this pipeline to PyPi has been automated, and it's done via the pypi_publish pipeline (`pypi-publish.yml` workflow). This pipeline authenticates against PyPi by using a token stored in the project's repo as `PYPI_API_TOKEN`.

The publishing pipeline executes the following command, retrieving the token from the project's secrets.

.. code-block:: bash

    pdm publish --username __token__ --password ${{ secrets.PYPI_API_TOKEN }}

Pre-Requisite
--------------

Save the PyPi token in the project's secrets as `PYPI_API_TOKEN`.

Details:
- `https://pypi.org/help/#apitoken`
- `https://guidebook.devops.uis.cam.ac.uk/en/latest/howtos/pypi/`
