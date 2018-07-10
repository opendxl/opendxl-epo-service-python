import socket
import re
import json
import ssl
import os
import uuid

try:
    from http.server import SimpleHTTPRequestHandler
    from socketserver import TCPServer
except ImportError:
    from SimpleHTTPServer import  SimpleHTTPRequestHandler
    from SocketServer import TCPServer

from threading import Thread

import requests

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

        if re.search(self.HELP_PATTERN, self.path):
            response_content = self.help_cmd()

        elif re.search(self.SYSTEM_FIND_PATTERN, self.path):
            response_content = self.system_find_cmd()

        elif re.search(self.SECURITY_TOKEN_PATTERN, self.path):
            response_content = self.security_token_cmd()

        elif re.search(self.STATUS_REPORT_PATTERN, self.path):
            response_content = self.dxlclient_statusreport_cmd()

        elif re.search("/helloworld", self.path):
            response_content = "Hello World"

        self.send_response(requests.codes.ok, response_content)

        self.send_header('Content-Type', 'text/plain; charset=utf-8', )
        self.end_headers()

        self.wfile.write(response_content.encode('utf-8'))

        return


    def help_cmd(self):
        listed_commands = "OK:\n"

        for cmd in self.KNOWN_COMMANDS:

            cmd_string = cmd["name"] + " "

            for param in cmd["parameters"]:
                cmd_string += "[" + param + "] "

            cmd_string += "- " + cmd["description"]

            listed_commands += cmd_string

        return listed_commands


    @staticmethod
    def system_find_cmd():

        return "OK:\n" + json.dumps(SYSTEM_FIND_PAYLOAD)


    @staticmethod
    def security_token_cmd():
        return "OK:\n" + TEST_SECURITY_TOKEN


    @staticmethod
    def dxlclient_statusreport_cmd():
        return 'OK:\n' \
               '{' \
                   '"keepAliveInterval" : 1800, ' \
                   '"productVersion" : "4.1.0.184",' \
                   '"uniqueId" : "{' + str(uuid.uuid4()) + '}"'\
               '}'


    @staticmethod
    def error_cmd(cmd_string):
        return ERROR_RESPONSE_PAYLOAD_PREFIX + str(cmd_string)


class MockServerRunner(object):

    def __init__(self, number_of_servers=1):
        self.number_of_servers = number_of_servers
        self.servers = []
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
            mock_server_thread.setDaemon(True)
            mock_server_thread.start()

            self.servers.append(
                mock_server
            )

            self.server_info_list.append(
                {
                    SERVER_INFO_SERVER_NAME_KEY: TEST_EPONAME_BASE + str(server_number),
                    SERVER_INFO_SERVER_PORT_KEY: mock_server_port,
                }
            )

        return self.server_info_list


    def __exit__(self, exc_type, exc_val, exc_tb):
        for server in self.servers:
            server.shutdown()
