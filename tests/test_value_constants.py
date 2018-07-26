import os

TEST_FOLDER = str(os.path.dirname(os.path.abspath(__file__)))
EPO_SERVICE_CONFIG_FILENAME = TEST_FOLDER + "/dxleposervice.config"

ERROR_RESPONSE_PAYLOAD_PREFIX = "Error 1 : \nNo such command: "

CORE_HELP_CMD_NAME = "core.help"
SYSTEM_FIND_OSTYPE_LINUX = "Linux"

HELP_CMD_RESPONSE_PAYLOAD = (
    "core.help [command] [prefix=<>] - Displays a list of all commands and help \n"
    "strings."
    "system.find [searchText] [searchNameOnly] - Finds systems in the System Tree"
)

SYSTEM_FIND_CMD_NAME = "system.find"

SYSTEM_FIND_PAYLOAD = [
    {
        "EPOBranchNode.AutoID": 4,
        "EPOComputerProperties.OSType": "Linux",
        "EPOComputerProperties.OSVersion": "4.9",
        "EPOComputerProperties.Vdi": 0,
        "EPOLeafNode.AgentGUID": "11111111-2222-3333-4444-555555555555",
        "EPOLeafNode.ManagedState": 1,
        "EPOLeafNode.Tags": "DXLBROKER, Server"
    },
    {
        "EPOBranchNode.AutoID": 4,
        "EPOComputerProperties.OSType": "Linux",
        "EPOComputerProperties.OSVersion": "4.9",
        "EPOComputerProperties.Vdi": 0,
        "EPOLeafNode.AgentGUID": "66666666-7777-8888-9999-000000000000",
        "EPOLeafNode.ManagedState": 1,
        "EPOLeafNode.Tags": "DXLBROKER, Server"
    }
]

TEST_GUID = "{00000000-1111-2222-3333-555555666666}"
TEST_SECURITY_TOKEN = "aaaaBBBBccccDDDD"
TEST_EPONAME_BASE = "testEpo"
LOCALHOST_IP = "127.0.0.1"
TEST_USER = "testUser"
TEST_PASSWORD = "testPassword"

SERVER_INFO_SERVER_NAME_KEY = "server_name"
SERVER_INFO_SERVER_PORT_KEY = "mock_server_port"
