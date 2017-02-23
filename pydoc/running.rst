Running Service
===============

Once the ePO DXL service module has been installed and the configuration files are populated it can be started by
executing the following command line:

    .. parsed-literal::

        python -m dxleposervice <configuration-directory>

    The ``<configuration-directory>`` argument must point to a directory containing the configuration files
    required for the ePO DXL service (see :doc:`configuration`).

For example:

    .. parsed-literal::

        python -m dxleposervice config

Output
------

The output from starting the service should appear similar to the following:

    .. parsed-literal::

        Running service ...
        Request topic '/mcafee/service/epo/remote/epo1' associated with ePO server: epo1
        Incoming message configuration: queueSize=1000, threadCount=10
        Attempting to connect to DXL fabric ...
        Connected to DXL fabric.
        Registering service ...
        Service registration succeeded.
        Waiting for requests ...

Part of the output includes the DXL `request topic` that is associated with each `ePO server` that is defined within
the service configuration file.

    .. parsed-literal::

        Request topic '/mcafee/service/epo/remote/epo1' associated with ePO server: epo1

The output above states that ``/mcafee/service/epo/remote/epo1`` is the request topic that is associated with
the ePO server ``epo1`` defined in the service configuration file. The last part of the request topic (``epo1``)
corresponds to the ``uniqueId`` property value for the ePO server in the configuration file.

The ``uniqueId`` property is optional. If a value for this property is not specified, the service will lookup
the unique GUID for the ePO server and use that for its unique identifier. For example:

    .. parsed-literal::

        GUID '{4d993fec-70e6-41e1-bd4e-3164c77d7c92}' found for ePO server: epo1
        Request topic '/mcafee/service/epo/remote/{4d993fec-70e6-41e1-bd4e-3164c77d7c92}' associated with ePO server: epo1

