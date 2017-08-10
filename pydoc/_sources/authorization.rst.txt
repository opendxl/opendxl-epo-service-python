Authorization
=============

A critical aspect of exposing ePO to the DXL fabric is adding an authorization policy that restricts which
clients can provide the service and which clients can invoke the service.

For an overview of DXL authorization, please see the following page:

`<https://opendxl.github.io/opendxl-client-python/pydoc/topicauthoverview.html>`_

**NOTE: As of DXL 3.0.1 certificate-based authentication and authorization information is not automatically replicated
between ePO servers. Therefore, the following steps must be repeated for each ePO server that is connected
to the DXL fabric.**

Create Topic Group
------------------

The first step is to create a `Topic Group` for the `ePO DXL Service`.

.. image:: addtopicgroup.png

As shown in the screenshot above, a `topic` should be added for each ePO server that is being exposed by the
ePO DXL service. The last portion of the topic matches the ``uniqueId`` associated with the ePO Server
(see :ref:`Service Configuration File <dxl_service_config_file_label>`).

Multiple topic groups can be created if different authorization policies are necessary for different ePO servers.

Service Authorization
---------------------

This section walks through the steps to restrict which clients can provide (run) the ePO DXL Service.

.. image:: restrictreceive.png

As show in the screenshot above, select the "ePO DXL Service" topic group and then select the
"Restrict Receive Certificates" action.

.. image:: restrictreceivecert.png

Next, select the certificate(s) associated with the clients that will be providing (running) the ePO DXL Service.
In the screenshot above, the certificate with the common name of "ePO DXL Service" is selected. Once the
appropriate certificates are selected click "OK".

.. image:: restrictsend.png

At this point we have restricted which clients can provide the ePO DXL service, but we have done nothing to restrict
which clients can invoke the service. The easiest thing to do is to limit the sending capability to the same
certificate that is providing the service. This effectively means that that no clients wil be able to invoke
the ePO DXL service.

There must always be send restrictions associated with the ePO DXL service. If no restrictions exist, all clients are
permitted to invoke the service.

As show in the screenshot above, select the "ePO DXL Service" topic group and then select the
"Restrict Send Certificates" action.

.. image:: restrictsendcert.png

Next, select the same certificates that were chosen in the previous step for restricting receive.
In the screenshot above, the certificate with the common name of "ePO DXL Service" is selected. Once the
appropriate certificates are selected click "OK".

.. _client_authorization:

Client Authorization
--------------------

This section walks through the steps to restrict which clients can invoke the ePO DXL Service.

.. image:: restrictsend2.png

As show in the screenshot above, select the "ePO DXL Service" topic group and then select the
"Restrict Send Certificates" action.

.. image:: restrictsendcert2.png

Next, select the certificates associated with the clients that are allowed to invoke the ePO DXL Service.
In the screenshot above, the certificates with common names of "ePO DXL Service" and
"ePO DXL Service Samples Client" are selected. Once the appropriate certificates are selected click "OK".
