Basic Core Help Example
========================

This sample invokes and displays the results of the "core help" remote command via the ePO DXL service.
The "core help" command lists the remote commands that are exposed by a particular ePO server.


Prerequisites
*************
* The samples configuration step has been completed (see :doc:`sampleconfig`)
* The ePO DXL service is running (see :doc:`running`)
* The client is authorized to invoke the ePO DXL Service (see :ref:`Client Authorization <client_authorization>`)

Setup
*****

Modify the example to include the `unique identifier` associated with the ePO to invoke the remote command on
(see :ref:`Service Configuration File <dxl_service_config_file_label>`).

For example:

    .. code-block:: python

        EPO_UNIQUE_ID = "epo1"

Running
*******

To run this sample execute the ``sample/basic/basic_core_help_example.py`` script as follows:

    .. parsed-literal::

        python sample/basic/basic_core_help_example.py

The output should appear similar to the following:

    .. code-block:: python

        ComputerMgmt.createAgentDeploymentUrlCmd deployPath groupId [edit] [ahId]
        [fallBackAhId] [urlName] [agentVersionNumber] [agentHotFix] - Create Agent
        Deployment URL Command
        ComputerMgmt.createCustomInstallPackageCmd deployPath [ahId] [fallBackAhId] -
        Create Custom Install Package Command
        ComputerMgmt.createDefaultAgentDeploymentUrlCmd tenantId - Create Default
        Non-Editable Agent Deployment URL Command
        ComputerMgmt.createTagGroup parentTagGroupId newTagGroupName - Create a new
        subgroup under an existing tag group.
        ComputerMgmt.deleteTag tagIds [forceDelete] - Delete one or more tags.
        ComputerMgmt.deleteTagGroup tagGroupIds [deleteTags] - Delete one or more Tag
        Groups.
        ComputerMgmt.listAllTagGroups - List All Tag Groups in Tag Group Tree
        ComputerMgmt.moveTagsToTagGroup tagIds tagGroupId - Move tags to an existing tag
        group.

        ...

Each remote command exposed by the particular ePO server is listed along with its associated parameters.

Details
*******

The majority of the sample code is shown below:

    .. code-block:: python

        # The ePO unique identifier
        EPO_UNIQUE_ID = "epo1"

        # Create the client
        with DxlClient(config) as client:

            # Connect to the fabric
            client.connect()

            # Create the request
            req = Request("/mcafee/service/epo/remote/{0}".format(EPO_UNIQUE_ID))

            # Set the payload for the request (core.help remote command)
            req.payload = \
                json.dumps({
                    "command": "core.help",
                    "output": "verbose",
                    "params": {}
                }).encode(encoding="utf-8")

            # Send the request
            res = client.sync_request(req, timeout=30)
            if res.message_type != Message.MESSAGE_TYPE_ERROR:
                # Display resulting payload
                print res.payload.decode(encoding='utf-8')
            else:
                print "Error: {0} ({1}) ".format(res.error_message, str(res.error_code))

After connecting to the DXL fabric, a `request message` is created with a topic that targets the ePO DXL service
including a unique identifier that is associated with the ePO server to invoke the remote command on.

The next step is to set the `payload` of the request message. The contents of the payload include the remote
command to invoke, the output style for the ePO server response (json, xml, verbose, or terse), and
any parameters for the command. In this particular case the ``core.help`` command is being invoked with an output
style of ``verbose``. This particular command requires no parameters, so an empty dictionary (``dict``) is specified.

The final step is to perform a `synchronous request` via the DXL fabric. If the `response message` is not an error
its contents are displayed.



