import socket
import re
import ssl
import uuid

try: #Python 3
    from http.server import SimpleHTTPRequestHandler
    from socketserver import TCPServer
    import urllib.parse as urlparse
except ImportError: #Python 2.7
    from SimpleHTTPServer import  SimpleHTTPRequestHandler
    from SocketServer import TCPServer
    import urlparse

from threading import Thread

import requests

from dxlbootstrap.util import MessageUtils
from tests.test_value_constants import *

TEST_FOLDER = str(os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"))
MOCK_EPOHTTPSERVER_CERTNAME = TEST_FOLDER + "/client.crt"
MOCK_EPOHTTPSERVER_KEYNAME = TEST_FOLDER + "/client.key"


def get_free_port():
    stream_socket = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    stream_socket.bind(('localhost', 0))
    address, port = stream_socket.getsockname()
    stream_socket.close()

    return address, port


class MockEpoServerRequestHandler(SimpleHTTPRequestHandler):

    HELP_PATTERN = re.compile(r'/remote/core.help')
    SYSTEM_FIND_PATTERN = re.compile(r'/remote/system.find')
    SECURITY_TOKEN_PATTERN = re.compile(r'/remote/core.getSecurityToken')
    STATUS_REPORT_PATTERN = re.compile(r'/remote/DxlClient.getStatusReport')

    SECURITY_TOKEN_PARAM = 'orion.user.security.token'
    SEARCH_TEXT_PARAM = 'searchText'

    KNOWN_COMMANDS = [
        {
            "name": "core.help",
            "parameters": [
                "command",
                "prefix=<>"
            ],
            "description": "Displays a list of all commands and help \nstrings."
        },
        {
            "name": "system.find",
            "parameters": [
                "searchText",
                "searchNameOnly"
            ],
            "description": "Finds systems in the System Tree"
        }
    ]


    def do_GET(self):
        response_content = self.error_cmd(re)

        parsed_url = urlparse.urlparse(self.path)

        if re.search(self.HELP_PATTERN, self.path):
            response_content = self.help_cmd()

        elif re.search(self.SYSTEM_FIND_PATTERN, self.path):
            response_content = self.system_find_cmd(parsed_url)

        elif re.search(self.SECURITY_TOKEN_PATTERN, self.path):
            response_content = self.security_token_cmd()

        elif re.search(self.STATUS_REPORT_PATTERN, self.path):
            response_content = self.dxlclient_statusreport_cmd(parsed_url)

        self.send_response(requests.codes.ok, response_content) #pylint: disable=no-member

        self.send_header('Content-Type', 'text/plain; charset=utf-8', )
        self.end_headers()

        self.wfile.write(response_content.encode('utf-8'))


    def help_cmd(self):
        listed_commands = "OK:\n"

        for cmd in self.KNOWN_COMMANDS:

            cmd_string = cmd["name"] + " "

            for param in cmd["parameters"]:
                cmd_string += "[" + param + "] "

            cmd_string += "- " + cmd["description"]

            listed_commands += cmd_string

        return listed_commands


    def system_find_cmd(self, parsed_url):
        parsed_search_text = \
            urlparse.parse_qs(parsed_url.query)[self.SEARCH_TEXT_PARAM][0]
        if SYSTEM_FIND_OSTYPE_LINUX == parsed_search_text:
            return "OK:\n" + MessageUtils.dict_to_json(SYSTEM_FIND_PAYLOAD)
        return self.bad_param(self.SEARCH_TEXT_PARAM, parsed_search_text)


    @staticmethod
    def security_token_cmd():
        return "OK:\n" + TEST_SECURITY_TOKEN


    def dxlclient_statusreport_cmd(self, parsed_url):
        parsed_security_token = \
            urlparse.parse_qs(parsed_url.query)[self.SECURITY_TOKEN_PARAM][0]

        if TEST_SECURITY_TOKEN in parsed_security_token:
            return 'OK:\n' \
                '{' \
                   '"keepAliveInterval" : 1800, ' \
                   '"productVersion" : "4.1.0.184",' \
                   '"uniqueId" : "{' + str(uuid.uuid4()) + '}"'\
                '}'
        return self.bad_param(self.SECURITY_TOKEN_PARAM, parsed_security_token)


    @staticmethod
    def error_cmd(cmd_string):
        return ERROR_RESPONSE_PAYLOAD_PREFIX + str(cmd_string)

    @staticmethod
    def bad_param(param_name, param_val):
        return MessageUtils.dict_to_json(
            {
                "unit_test_bad_param_name": param_name,
                "unit_test_bad_param_val": param_val
            },
            pretty_print=False
        )


class MockServerRunner(object):

    def __init__(self, number_of_servers=1):
        self.number_of_servers = number_of_servers
        self.servers = {}
        self.server_info_list = []
        self.mock_server_address = ""

    def __enter__(self):
        for server_number in range(self.number_of_servers):
            self.mock_server_address, mock_server_port = get_free_port()
            mock_server = TCPServer(
                ('localhost', mock_server_port),
                MockEpoServerRequestHandler
            )
            mock_server.socket = ssl.wrap_socket(
                mock_server.socket,
                certfile=MOCK_EPOHTTPSERVER_CERTNAME,
                keyfile=MOCK_EPOHTTPSERVER_KEYNAME,
                server_side=True
            )

            mock_server_thread = Thread(target=mock_server.serve_forever)

            self.servers[server_number] = {
                "server": mock_server,
                "thread": mock_server_thread
            }

            self.servers[server_number]["thread"].setDaemon(True)
            self.servers[server_number]["thread"].start()

            self.server_info_list.append(
                {
                    SERVER_INFO_SERVER_NAME_KEY: TEST_EPONAME_BASE + str(server_number),
                    SERVER_INFO_SERVER_PORT_KEY: mock_server_port,
                }
            )

        return self.server_info_list


    def __exit__(self, exc_type, exc_val, exc_tb):
        for server_number in self.servers:
            self.servers[server_number]["server"].shutdown()
            self.servers[server_number]["thread"].join()
