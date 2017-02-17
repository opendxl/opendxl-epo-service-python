# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

import json
import logging
import requests
import warnings
from requests.auth import HTTPBasicAuth

# Configure local logger
logger = logging.getLogger(__name__)


class _Epo(object):
    """
    An ePO server that is being wrapped and exposed to the DXL fabric
    """

    # The command used to determine the GUID for the ePO server
    DXL_CLIENT_STATUS_REPORT_COMMAND = "DxlClient.getStatusReport"

    # The key within the status report used to determine the ePO server's
    # unique identifier (GUID)
    UNIQUE_ID_KEY = "uniqueId"

    # UTF-8 encoding (used for encoding/decoding payloads)
    UTF_8 = "utf-8"

    def __init__(self, name, host, port, user, password, verify):
        """
        Constructs the ePO server wrapper

        :param name: The name of the ePO server
        :param host: The host for the ePO server
        :param port: The port for the ePO server
        :param user: The user used to login to the ePO server
        :param password: The password used to login to the ePO server
        :param verify: Whether to verify the ePO server's certificate
        """
        self._name = name
        self._client = _EpoRemote(host, port, user, password, verify)

    def lookup_guid(self):
        """
        Attempts to lookup the GUID (unique identifier) for the ePO server by invoking
        the "client status report" remote command

        :return: The GUID if found (otherwise an exception will be thrown)
        """
        try:
            response = self._client.invoke_command(self.DXL_CLIENT_STATUS_REPORT_COMMAND,
                                                   {}, output="json")
            response_dict = json.loads(response.decode(self.UTF_8))

            if self.UNIQUE_ID_KEY not in response_dict:
                raise Exception("Unable to find '{0}' in response.".format(self.UNIQUE_ID_KEY))

            return response_dict[self.UNIQUE_ID_KEY]
        except:
            logger.error("Error attempting to lookup GUID for ePO server: {0}".format(self._name))
            raise

    def execute(self, command, output, req_params):
        """
        Invokes a remote command on the ePO server (via HTTP)

        :param command: The command to invoke
        :param output: The output type (json, xml, verbose, terse)
        :param req_params: The parameters for the command
        :return: The result of the command execution
        """
        return self._client.invoke_command(command, req_params, output)


class _EpoRemote(object):
    """
    Handles REST invocation of ePO remote commands
    """

    def __init__(self, host, port, username, password, verify):
        """
        Initializes the epoRemote with the information for the target ePO instance

        :param host: the hostname of the ePO to run remote commands on
        :param port: the port of the desired ePO
        :param username: the username to run the remote commands as
        :param password: the password for the ePO user
        :param verify: Whether to verify the ePO server's certificate
        """

        logger.debug('Initializing epoRemote for ePO {} on port {} with user {}'.format(host, port, username))

        self._baseurl = 'https://{}:{}/remote'.format(host, port)
        self._auth = HTTPBasicAuth(username, password)
        self._session = requests.Session()
        self._verify = verify

    def invoke_command(self, command_name, params, output='json'):
        """
        Invokes the given remote command by name with the supplied parameters

        :param command_name: The name of the ePO remote command to invoke
        :param params: A dict of parameters to pass to the remote command
        :param output: the desired output format. Valid output types: json, xml, verbose, and terse
        :return: the response for the ePO remote command
        """

        if output not in ['json', 'xml', 'verbose', 'terse']:
            raise Exception('Invalid output type specified: ' + output)

        self._save_token()

        params['orion.user.security.token'] = self._token
        params[':output'] = output

        return self._parse_response(self._send_request(command_name, params))

    def _send_request(self, command_name, params=None):
        """
        Sends a request to the ePO server with the supplied command name and parameters

        :param command_name: The command name to invoke
        :param params: The parameters to provide for the command
        :return: the response object from ePO
        """
        logger.debug('Invoking command {} with the following parameters:'.format(command_name))
        logger.debug(params)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", ".*subjectAltName.*")
            if not self._verify:
                warnings.filterwarnings("ignore", "Unverified HTTPS request")
            return self._session.get('{}/{}'.format(self._baseurl, command_name),
                                     auth=self._auth,
                                     params=params,
                                     verify=self._verify)

    def _save_token(self):
        """
        Retrieves the security token for this session and saves it for later requests
        """
        self._token = self._parse_response(self._send_request('core.getSecurityToken'))
        logger.debug('Security token received from ePO: {}'.format(self._token))

    @staticmethod
    def _parse_response(response):
        """
        Parses the response object from ePO. Removes the return status and code from the response body and returns
        just the remote command response. Throws an exception if an error response is returned.

        :param response: the ePO remote command response object to parse
        :return: the ePO remote command results as a string
        """
        try:
            response_body = response.text

            logger.debug('Response from ePO: ' + response_body)
            status = response_body[:response_body.index(':')]
            result = response_body[response_body.index(':')+1:].strip()

            if 'Error' in status:
                code = int(status[status.index(' '):].strip())
                raise Exception('Response failed with error code ' + str(code) + '. Message: ' + result)

            return result
        except:
            logger.error('Exception while parsing response.')
            raise
