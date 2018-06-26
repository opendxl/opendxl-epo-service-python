import os
import sys
import uuid
import json

from configparser import ConfigParser
from dxlclient import Request
from dxleposervice import EpoService
from tests.test_base import BaseEpoServerTest
from tests.test_value_constants import *
from tests.mock_dxlclient import MockDxlClient
from tests.mock_epohttpserver import start_mock_epo_server

import dxleposervice._epo
import dxleposervice.app

sys.path.append(
    os.path.dirname(os.path.abspath(__file__)) + "/../.."
)

TEST_FOLDER = str(os.path.dirname(os.path.abspath(__file__)))
EPO_SERVICE_CONFIG_FILENAME = TEST_FOLDER + "/dxleposervice.config"

def create_eposervice_configfile(config_file_name, server_list):
    config = ConfigParser()

    server_names_string = ""

    for server_index, server in enumerate(server_list):
        if server_index > 0:
            server_names_string += ", "
        server_names_string += server[SERVER_INFO_SERVER_NAME_KEY]

        config[server[SERVER_INFO_SERVER_NAME_KEY]] = {
            'host': LOCALHOST_IP,
            'port': str(server[SERVER_INFO_SERVER_PORT_KEY]),
            'user': TEST_USER,
            'password': TEST_PASSWORD,
            'verifyCertificate': 'False'
        }

    config['General'] = {'epoNames': server_names_string}

    with open(config_file_name, 'w') as config_file:
        config.write(config_file)


class TestEpoServiceConfiguration(BaseEpoServerTest):

    def test_loadconfig(self):
        server_list = start_mock_epo_server(5)

        create_eposervice_configfile(
            config_file_name=EPO_SERVICE_CONFIG_FILENAME,
            server_list=server_list
        )

        # ---remember patch for later---
        # Patch USERS_URL so that the service uses the mock server URL instead of the real URL.
        #   with patch.dict('project.services.__dict__', {'USERS_URL': mock_users_url}):
        #   response = get_users()

        epo_service = EpoService(TEST_FOLDER)
        epo_service._load_configuration()

        epo_config_data = epo_service._epo_by_topic

        for epo in epo_config_data:
            expected_server_data = \
                next(item for item in server_list
                     if item[SERVER_INFO_SERVER_NAME_KEY] == epo_config_data[epo]._name
                    )

            self.assertEqual(
                epo_config_data[epo]._client._auth.password,
                TEST_PASSWORD
            )
            self.assertEqual(
                epo_config_data[epo]._client._auth.username,
                TEST_USER
            )
            self.assertEqual(
                epo_config_data[epo]._client._baseurl,
                'https://' + LOCALHOST_IP + ':'
                + str(expected_server_data[SERVER_INFO_SERVER_PORT_KEY])
                + '/remote'
            )
            self.assertIn(TEST_SECURITY_TOKEN, epo_config_data[epo]._client._token)


    def test_registerservices(self):
        server_list = start_mock_epo_server(number_of_servers=5)

        create_eposervice_configfile(
            config_file_name=EPO_SERVICE_CONFIG_FILENAME,
            server_list=server_list
        )

        with self.create_client(max_retries=0) as dxl_client:
            dxl_client.connect()

            epo_service = EpoService(TEST_FOLDER)
            epo_service._dxl_client = dxl_client

            epo_service._load_configuration()
            epo_service.on_register_services()

            self.assertTrue(len(epo_service._dxl_service.topics) > 0)

            for topic in epo_service._dxl_service.topics:
                remaining_uuid = str(topic).replace('/mcafee/service/epo/remote/', '')

                # Try to create a new UUID using remaining string,
                # will fail with a FormatException if string is not
                # a valid GUID
                uuid.UUID(remaining_uuid)


    def test_getoption(self):
        config = ConfigParser()
        correct_value = 'Correct'

        config['TestSection1'] = \
            {
                'TestOption1': 'Correct',
                'TestOption2': 'Incorrect_1-2'
            }
        config['TestSection2'] = \
            {
                'TestOption1': 'Incorrect_2-1',
                'TestOption2': 'Incorrect_2-2'
            }

        result = EpoService._get_option(
            config=config,
            section='TestSection1',
            option='TestOption1',
            default_value='DefaultValue'
        )

        self.assertEqual(correct_value, result)


    def test_getoption_default(self):
        config = ConfigParser()
        default_value = 'DefaultValue'

        config['TestSection1'] = \
            {
                'TestOption1': 'Correct',
                'TestOption2': 'Incorrect_1-2'
            }
        config['TestSection2'] = \
            {
                'TestOption1': 'Incorrect_2-1',
                'TestOption2': 'Incorrect_2-2'
            }

        result = EpoService._get_option(
            config=config,
            section='TestSection1',
            option='TestOption3',
            default_value=default_value
        )

        self.assertEqual(default_value, result)


    def test_getbooleanoption(self):
        config = ConfigParser()

        config['TestSection1'] = \
            {
                'TestOption1': 'True',
                'TestOption2': 'False'
            }
        config['TestSection2'] = \
            {
                'TestOption1': 'False',
                'TestOption2': 'False'
            }

        result = EpoService._get_boolean_option(
            config=config,
            section='TestSection1',
            option='TestOption1',
        )

        self.assertTrue(result)


    def test_getbooleanoption_default(self):
        config = ConfigParser()

        config['TestSection1'] = \
            {
                'TestOption1': 'True',
                'TestOption2': 'True'
            }
        config['TestSection2'] = \
            {
                'TestOption1': 'True',
                'TestOption2': 'True'
            }

        result = EpoService._get_boolean_option(
            config=config,
            section='TestSection1',
            option='TestOption3',
        )

        self.assertFalse(result)


class TestEpoRequestCallback(BaseEpoServerTest):

    def test_eporequestcallback(self):

        mock_dxl_client = MockDxlClient()
        server_info = start_mock_epo_server()[0]
        test_topic = "/test/topic"

        epo = dxleposervice._epo._Epo(
            server_info[SERVER_INFO_SERVER_NAME_KEY],
            LOCALHOST_IP,
            server_info[SERVER_INFO_SERVER_PORT_KEY],
            TEST_USER,
            TEST_PASSWORD,
            False
        )

        epo_topics = {test_topic: epo}

        class TestFirstInstanceCallback(dxleposervice.app._EpoRequestCallback):

            def __init__(self, dxl_client, epo_topics):
                dxleposervice.app._EpoRequestCallback.__init__(
                    self,
                    dxl_client,
                    epo_topics
                )

        test_request = Request(test_topic)

        # Set the payload
        test_request.payload = json.dumps(
            {
                "command": "core.help",
                "output": "json",
                "params": {}
            }
        ).encode(encoding="UTF-8")

        epo_request_callback = TestFirstInstanceCallback(mock_dxl_client, epo_topics)

        epo_request_callback.on_request(test_request)

        self.assertIn(
            HELP_CMD_RESPONSE_PAYLOAD,
            mock_dxl_client.latest_sent_message._payload
        )
