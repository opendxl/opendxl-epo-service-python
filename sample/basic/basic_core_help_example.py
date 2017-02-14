# This sample invokes and displays the results of the "core help" remote
# command via the ePO DXL service. The "core help" command lists the
# remote commands that are exposed by the particular ePO server.
#
# NOTE: Prior to running this sample you must provide a value for the following
#       constant in this file:
#
#       EPO_UNIQUE_ID : The unique identifier used to identify the ePO server
#                       on the DXL fabric.

import json
import os
import sys

from dxlclient.client_config import DxlClientConfig
from dxlclient.client import DxlClient
from dxlclient.message import Request, Message

# Import common logging and configuration
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from common import *

# Configure local logger
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Create DXL configuration from file
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)

# The ePO unique identifier
EPO_UNIQUE_ID = "<specify-ePO-unique-identifier>"

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
