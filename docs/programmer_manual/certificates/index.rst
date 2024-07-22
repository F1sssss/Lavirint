Working with certificates
=========================

Retrieving certificates from server
-----------------------------------

Use SSH to connect to remote server. Navigate to the root of backend directory. 

Run following command is used to retrieve certificate:

.. code:: bash

    . environment.sh && python3 -m backend.cli certificate.info --help

    Usage: python -m backend.cli certificate:info [OPTIONS] ID_NUMBER

    Options:
    --id    Get info by company id
    --tin   Get info by company tin
    --help  Show this message and exit.

The command outputs JSON which contains password and absolute path to certificate file:

.. code:: JSON

    {
        "password": "y23has78",
        "path": "/example/path/to/certificate.pfx"
    }

Use ``scp`` command to download certificate.


Installing certificate on Windows
---------------------------------

Run terminal and navigate to folder which contains certificate you want to import. Run following command:

.. code:: bash

    CERTUTIL -user -f -p "password" -importpfx certificate.pfx