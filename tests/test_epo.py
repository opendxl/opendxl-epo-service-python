import os
import sys
import uuid
import requests

from tests.test_base import BaseClientTest
from tests.test_value_constants import *
from tests.mock_epohttpserver import MockServerRunner

import dxleposervice._epo

sys.path.append(
    os.path.dirname(os.path.abspath(__file__)) + "/../.."
)

class TestEpo(BaseClientTest):

    def test_execute(self):
        with MockServerRunner() as server_list:
            server_info = server_list[0]

            epo = dxleposervice._epo._Epo(
                name=server_info[SERVER_INFO_SERVER_NAME_KEY],
                host=LOCALHOST_IP,
                port=server_info[SERVER_INFO_SERVER_PORT_KEY],
                user=TEST_USER,
                password=TEST_PASSWORD,
                verify=False
            )

            result = epo.execute(
                command='core.help',
                output='json',
                req_params={}
            )

            self.assertIn('system.find', result)

    def test_lookupguid(self):
        with MockServerRunner() as server_list:
            server_info = server_list[0]

            epo = dxleposervice._epo._Epo(
                name=server_info[SERVER_INFO_SERVER_NAME_KEY],
                host=LOCALHOST_IP,
                port=server_info[SERVER_INFO_SERVER_PORT_KEY],
                user=TEST_USER,
                password=TEST_PASSWORD,
                verify=False
            )

            result = epo.lookup_guid()

            result_uuid = uuid.UUID(result)

            self.assertIsInstance(result_uuid, uuid.UUID)


class TestEpoRemote(BaseClientTest):

    def test_invokecommand(self):
        with MockServerRunner() as server_list:
            server_info = server_list[0]

            epo_remote = dxleposervice._epo._EpoRemote(
                host=LOCALHOST_IP,
                port=server_info[SERVER_INFO_SERVER_PORT_KEY],
                username=TEST_USER,
                password=TEST_PASSWORD,
                verify=False
            )

            result = epo_remote.invoke_command(
                command_name='core.help',
                params={},
                output='json'
            )

            self.assertIn('system.find', result)


    def test_sendrequest(self):
        with MockServerRunner() as server_list:
            server_info = server_list[0]

            epo_remote = dxleposervice._epo._EpoRemote(
                host=LOCALHOST_IP,
                port=server_info[SERVER_INFO_SERVER_PORT_KEY],
                username=TEST_USER,
                password=TEST_PASSWORD,
                verify=False
            )

            result = epo_remote._send_request(
                command_name='core.help',
                params={}
            )

            self.assertIn('system.find', result.content.decode('utf-8'))


    def test_parseresponse(self):
        input_response = requests.Response()
        input_response._content = \
            'RandomServerInfo_!@#$^&*()_+:GeneratedSecurityToken'.encode('utf-8')

        result = dxleposervice._epo._EpoRemote._parse_response(input_response)

        self.assertEqual(u'GeneratedSecurityToken', result)
