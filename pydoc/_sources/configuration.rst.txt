Service Configuration
=====================

The ePO DXL service requires a set of configuration files to operate.

This distribution contains a ``config`` sub-directory that includes the configuration files that must
be populated prior to running the service.

Each of these files are documented throughout the remained of this page.

Service configuration directory:

    .. code-block:: python

        config/
            dxlclient.config
            dxleposervice.config
            logging.config (optional)

.. _dxl_client_config_file_label:

DXL Client Configuration File (dxlclient.config)
------------------------------------------------

    The required ``dxlclient.config`` file is used to configure the DXL client that will connect to the DXL fabric
    and expose the ePO DXL service.

    The steps to populate this configuration file are the same as those documented in the `OpenDXL Python
    SDK`, see the
    `OpenDXL Python SDK Samples Configuration <https://opendxl.github.io/opendxl-client-python/pydoc/sampleconfig.html>`_
    page for more information.

    The following is an example of a populated DXL client configuration file:

        .. code-block:: python

            [Certs]
            BrokerCertChain=c:\\certificates\\brokercerts.crt
            CertFile=c:\\certificates\\client.crt
            PrivateKey=c:\\certificates\\client.key

            [Brokers]
            {5d73b77f-8c4b-4ae0-b437-febd12facfd4}={5d73b77f-8c4b-4ae0-b437-febd12facfd4};8883;mybroker.mcafee.com;192.168.1.12
            {24397e4d-645f-4f2f-974f-f98c55bdddf7}={24397e4d-645f-4f2f-974f-f98c55bdddf7};8883;mybroker2.mcafee.com;192.168.1.13

.. _dxl_service_config_file_label:

DXL Service Configuration File (dxleposervice.config)
-----------------------------------------------------

    The required ``dxleposervice.config`` file is used to configure the ePO DXL Service. Specifically, it is
    used to specify information about the ePO servers whose remote commands will be exposed to the DXL fabric.

    The following is an example of a populated ePO DXL service configuration file:

        .. code-block:: python

            [General]
            epoNames=epo1

            [epo1]
            host=epotestsystem
            port=8443
            user=admin
            password=password
            uniqueId=epo1
            verifyCertificate=yes
            verifyCertBundle=epoCA.crt

    **General Section**

        The ``[General]`` section is used to specify the list of ePO servers to expose to the DXL fabric. Multiple
        ePO servers can be exposed via a single ePO DXL service instance.

        +------------------------+----------+--------------------------------------------------------------------+
        | Name                   | Required | Description                                                        |
        +========================+==========+====================================================================+
        | epoNames               | yes      | The list of ePO servers to expose to the DXL fabric delimited by   |
        |                        |          | commas.                                                            |
        |                        |          |                                                                    |
        |                        |          | For example: ``epo1,epo2,epo3``                                    |
        |                        |          |                                                                    |
        |                        |          | For each ePO name specified, a corresponding section must be       |
        |                        |          | defined within this configuration file that provides detailed      |
        |                        |          | information about the server (see "ePO Section" below).            |
        +------------------------+----------+--------------------------------------------------------------------+

    **ePO Section (1 per ePO server)**

        Each ePO server specified in the ``epoNames`` property of the ``[General]`` section must have a
        section defined which contains details about the particular server.

        The section name must match the name of the ePO in the ``epoNames`` property (for example: ``[epo1]``).

        +------------------------+----------+--------------------------------------------------------------------+
        | Name                   | Required | Description                                                        |
        +========================+==========+====================================================================+
        | host                   | yes      | The hostname (or IP address) of the ePO Server to expose to the    |
        |                        |          | DXL fabric.                                                        |
        |                        |          |                                                                    |
        |                        |          | **NOTE: If the** ``verifyCertificate`` **property is set to**      |
        |                        |          | ``yes`` **the host value must match the "CN value" in the ePO      |
        |                        |          | server's certificate.**                                            |
        +------------------------+----------+--------------------------------------------------------------------+
        | port                   | no       | The ePO server communication port.                                 |
        |                        |          |                                                                    |
        |                        |          | Port is optional and defaults to ``8443`` if not specified.        |
        +------------------------+----------+--------------------------------------------------------------------+
        | user                   | yes      | The name of the user used to login to the ePO server.              |
        |                        |          |                                                                    |
        |                        |          | This user will be used to invoke remote commands on this server.   |
        |                        |          |                                                                    |
        |                        |          | **NOTE: All of the remote commands available to the specified user |
        |                        |          | will be exposed to the fabric. Thus, it is important to select     |
        |                        |          | a user that only exposes the desired remote commands to the DXL    |
        |                        |          | fabric (and nothing additional).**                                 |
        +------------------------+----------+--------------------------------------------------------------------+
        | password               | yes      | The password associated with the user used to login to the ePO     |
        |                        |          | server.                                                            |
        +------------------------+----------+--------------------------------------------------------------------+
        | uniqueId               | no       | A unique identifier used to identify the ePO server on the DXL     |
        |                        |          | fabric.                                                            |
        |                        |          |                                                                    |
        |                        |          | The unique identifier is optional and will default to the GUID of  |
        |                        |          | the ePO server if not specified.                                   |
        |                        |          |                                                                    |
        |                        |          | This unique identifier will be the last portion of the request     |
        |                        |          | topic that is used to invoke remote commands on this ePO server    |
        |                        |          | via the DXL fabric.                                                |
        |                        |          |                                                                    |
        |                        |          | For example: ``/mcafee/service/epo/remote/epo1``                   |
        +------------------------+----------+--------------------------------------------------------------------+
        | verifyCertificate      | no       | Whether to verify that the hostname in the ePO's certificate       |
        |                        |          | matches the ePO server being connected to and that the certificate |
        |                        |          | was signed by a valid authority.                                   |
        |                        |          |                                                                    |
        |                        |          | Verify certificate is optional and will default to enabled if not  |
        |                        |          | specified.                                                         |
        |                        |          |                                                                    |
        |                        |          | **NOTE: This property should only be disabled for testing purposes |
        |                        |          | (never for a production environment).**                            |
        +------------------------+----------+--------------------------------------------------------------------+
        | verifyCertBundle       | no       | A path to a CA Bundle file containing certificates                 |
        |                        |          | of trusted CAs. The CA Bundle is used to ensure that the           |
        |                        |          | ePO server being connected to was signed by a valid authority.     |
        |                        |          |                                                                    |
        |                        |          | This property is only applicable if the ``verityCertificate``      |
        |                        |          | property is set to ``yes``.                                        |
        +------------------------+----------+--------------------------------------------------------------------+

Logging File (logging.config)
-----------------------------

    The optional ``logging.config`` file is used to configure how the ePO DXL Service writes log messages.