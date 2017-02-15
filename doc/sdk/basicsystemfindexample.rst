Basic System Find Example
=========================

This sample invokes and displays the results of a "system find" remote command via the ePO DXL service.
The results of the find command are displayed in JSON format.

Prerequisites
*************
* The samples configuration step has been completed (see :doc:`sampleconfig`)
* The ePO DXL service is running (see :doc:`running`)
* The client is authorized to invoke the ePO DXL Service (see :ref:`Client Authorization <client_authorization>`)
* The user that is connecting to the ePO server has permission to execute the "system find" remote command
  (see :ref:`Service Configuration File <dxl_service_config_file_label>`).

Setup
*****

Modify the example to include the `unique identifier` associated with the ePO to invoke the remote command on
(see :ref:`Service Configuration File <dxl_service_config_file_label>`).

For example:

    .. code-block:: python

        EPO_UNIQUE_ID = "epo1"

Modify the example to include the search text for the system find command.

For example:

    .. code-block:: python

        SEARCH_TEXT = "broker"


Running
*******

To run this sample execute the ``sample/basic/basic_system_find_example.py`` script as follows:

    .. parsed-literal::

        python sample/basic/basic_system_find_example.py

The output should appear similar to the following:

    .. code-block:: python

        [
            {
                "EPOBranchNode.AutoID": 7,
                "EPOComputerProperties.CPUSerialNum": "N/A",
                "EPOComputerProperties.CPUSpeed": 2794,
                "EPOComputerProperties.CPUType": "Intel(R) Core(TM) i7-4980HQ CPU @ 2.80GHz",
                "EPOComputerProperties.ComputerName": "broker1",
                "EPOComputerProperties.DefaultLangID": "0409",
                "EPOComputerProperties.Description": null,

                ...
            }
        ]

The properties for each system found will be displayed.

Details
*******

The majority of the sample code is shown below:

    .. code-block:: python

        # The ePO unique identifier
        EPO_UNIQUE_ID = "epo1"

        # The search text
        SEARCH_TEXT = "broker"

        # Create the client
        with DxlClient(config) as client:

            # Connect to the fabric
            client.connect()

            req = Request("/mcafee/service/epo/remote/{0}".format(EPO_UNIQUE_ID))

            req.payload = \
                json.dumps({
                    "command": "system.find",
                    "output": "json",
                    "params": {"searchText": SEARCH_TEXT}
                }).encode(encoding="utf-8")

            # Send the request
            res = client.sync_request(req, timeout=30)
            if res.message_type != Message.MESSAGE_TYPE_ERROR:
                response_dict = json.loads(res.payload, encoding='utf-8')
                print json.dumps(response_dict, sort_keys=True, indent=4, separators=(',', ': '))
            else:
                print "Error: {0} ({1}) ".format(res.error_message, str(res.error_code))

After connecting to the DXL fabric, a `request message` is created with a topic that targets the ePO DXL service
including a unique identifier that is associated with the ePO server to invoke the remote command on.

The next step is to set the `payload` of the request message. The contents of the payload include the remote
command to invoke, the output style for the ePO server response (json, xml, verbose, or terse), and
any parameters for the command. In this particular case the ``system.find`` command is being invoked with an output
style of ``json``. A ``searchText`` parameter is specified with the value of ``broker``.

The final step is to perform a `synchronous request` via the DXL fabric. If the `response message` is not an error,
the resulting JSON is loaded into a Python dictionary (``dict``) and ultimately displayed to the screen.



