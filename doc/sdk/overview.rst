Overview
========


The `McAfee ePolicy Orchestrator <https://www.mcafee.com/us/products/epolicy-orchestrator.aspx>`_ (ePO) DXL Python
service exposes access to ePO remote commands via the `Data Exchange Layer <http://www.mcafee.com/us/solutions/data-exchange-layer.aspx>`_
(DXL) fabric.

The purpose of this service is to allow users to invoke ePO remote commands via the DXL fabric.

.. image:: eposervice.png

As shown in the figure above, a single ePO DXL service can be configured to provide access to the remote commands
exposed by one or more ePO servers.

DXL clients can invoke ePO remote commands by sending DXL request messages via the DXL fabric.
The ePO DXL service handles incoming request messages and forwards them to the appropriate ePO server via secure HTTP.
Responses received from the ePO server are packaged by the ePO DXL service as DXL response messages and sent back
to the invoking DXL client.