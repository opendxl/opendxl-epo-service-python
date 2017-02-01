# This sample invokes and displays the results of the "core help" command via
# the ePO DXL service. This displays the remote commands that are exposed by
# the ePO server.
#
# NOTE: Prior to running this sample you must provide values for the following
#       constants in this file:
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

# The DXL request prefix for invoking remote commands
DXL_REQUEST_PREFIX = "/mcafee/service/epo/remote/"

# The ePO unique identifier
EPO_UNIQUE_ID = "<specify-ePO-unique-identifier>"

# Create the client
with DxlClient(config) as client:

    # Connect to the fabric
    client.connect()

    req = Request(''.join([DXL_REQUEST_PREFIX, EPO_UNIQUE_ID]))

    req.payload = \
        json.dumps({
            "command": "core.help",
            "output": "verbose",
            "params": {}
        }).encode(encoding="utf-8")

    # Send the request
    res = client.sync_request(req)
    if res.message_type != Message.MESSAGE_TYPE_ERROR:
        print res.payload.decode(encoding='utf-8')
    else:
        print "Error: {0} ({1}) ".format(res.error_message, str(res.error_code))
