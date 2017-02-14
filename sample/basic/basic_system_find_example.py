# This sample invokes and displays the results of the "system find" command via
# the ePO DXL service. The results of the find command are displayed in JSON
# format.
#
# NOTE: Prior to running this sample you must provide values for the following
#       constants in this file:
#
#       EPO_UNIQUE_ID : The unique identifier used to identify the ePO server
#                       on the DXL fabric.
#
#       SEARCH_TEXT   : The search text to use (system name, etc.)

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

# The search text
SEARCH_TEXT = "<specify-find-search-text>"

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
