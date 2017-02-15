# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

import logging
import os
import json
from threading import Lock

from ConfigParser import ConfigParser, NoOptionError

from dxlclient.client import DxlClient
from dxlclient.client_config import DxlClientConfig
from dxlclient.service import ServiceRegistrationInfo
from dxlclient.callbacks import RequestCallback
from dxlclient.message import ErrorResponse, Response

from _epo import _Epo

# Configure local logger
logger = logging.getLogger(__name__)


class EpoService(object):
    """
    A DXL service that exposes the remote commands of one or more ePO servers to
    the DXL fabric. When a DXL request message is received, the remote command is invoked
    on the appropriate ePO server and its response is packaged and returned to the invoking
    client via a DXL response message.
    """

    # The name of the DXL client configuration file
    DXL_CLIENT_CONFIG_FILE = "dxlclient.config"
    # The name of the ePO service configuration file
    DXL_EPO_SERVICE_CONFIG_FILE = "dxleposervice.config"

    # The type of the ePO DXL service that is registered with the fabric
    DXL_SERVICE_TYPE = "/mcafee/service/epo/remote"
    # The format for request topics that are associated with the ePO DXL service
    DXL_REQUEST_FORMAT = "/mcafee/service/epo/remote/{0}"
    # The timeout used when registering/unregistering the service
    DXL_SERVICE_REGISTRATION_TIMEOUT = 60

    # The name of the "General" section within the ePO service configuration file
    GENERAL_CONFIG_SECTION = "General"
    # The property used to specify ePO names within the "General" section of the
    # ePO service configuration file
    GENERAL_EPO_NAMES_CONFIG_PROP = "epoNames"

    # The property used to specify the host of an ePO within within the ePO service
    # configuration file
    EPO_HOST_CONFIG_PROP = "host"
    # The property used to specify the port of an ePO server within the ePO service
    # configuration file (this property is optional)
    EPO_PORT_CONFIG_PROP = "port"
    # The property used to specify the user used to login to an ePO server within
    # the ePO service configuration file
    EPO_USER_CONFIG_PROP = "user"
    # The property used to specify the password used to login to an ePO server within the ePO
    # service configuration file
    EPO_PASSWORD_CONFIG_PROP = "password"
    # The property used to specify the unique identifier for the ePO server within
    # the ePO service configuration file (this property is optional)
    EPO_UNIQUE_ID_CONFIG_PROP = "uniqueId"
    # Whether to verify that the hostname in the ePO's certificate matches the ePO
    # server being connected to. (optional, enabled by default)
    EPO_VERIFY_CERTIFICATE = "verifyCertificate"
    # A path to a CA Bundle file containing certificates of trusted CAs.
    # The CA Bundle is used to ensure that the ePO server being connected to was signed by a
    # valid authority.
    EPO_VERIFY_CERT_BUNDLE = "verifyCertBundle"

    # Default value for verifying certificates
    DEFAULT_VERIFY_CERTIFICATE = True

    # The default port used to communicate with an ePO server
    DEFAULT_EPO_PORT = 8443

    # The name of the "IncomingMessagePool" section within the ePO service
    # configuration file
    INCOMING_MESSAGE_POOL_CONFIG_SECTION = "IncomingMessagePool"
    # The property used to specify the queue size for the incoming message pool
    INCOMING_MESSAGE_POOL_QUEUE_SIZE_CONFIG_PROP = "queueSize"
    # The property used to specify the thread count for the incoming message pool
    INCOMING_MESSAGE_POOL_THREAD_COUNT_CONFIG_PROP = "threadCount"

    # The default thread count for the incoming message pool
    DEFAULT_THREAD_COUNT = 10
    # The default queue size for the incoming message pool
    DEFAULT_QUEUE_SIZE = 1000

    def __init__(self, config_dir):
        """
        Constructor parameters:

        :param config_dir: The location of the configuration files for the ePO service
        """
        self._config_dir = config_dir
        self._dxlclient_config_path = os.path.join(config_dir, self.DXL_CLIENT_CONFIG_FILE)
        self._dxleposervice_config_path = os.path.join(config_dir, self.DXL_EPO_SERVICE_CONFIG_FILE)
        self._epo_by_topic = {}
        self._dxl_client = None
        self._dxl_service = None
        self._running = False
        self._destroyed = False

        self._incoming_thread_count = self.DEFAULT_THREAD_COUNT
        self._incoming_queue_size = self.DEFAULT_QUEUE_SIZE

        self._lock = Lock()

    def __del__(self):
        """destructor"""
        self.destroy()

    def __enter__(self):
        """Enter with"""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit with"""
        self.destroy()

    def _validate_config_files(self):
        """
        Validates the configuration files necessary for the ePO service. An exception is thrown
        if any of the required files are inaccessible.
        """
        if not os.access(self._dxlclient_config_path, os.R_OK):
            raise Exception(
                "Unable to access client configuration file: {0}".format(
                    self._dxlclient_config_path))
        if not os.access(self._dxleposervice_config_path, os.R_OK):
            raise Exception(
                "Unable to access service configuration file: {0}".format(
                    self._dxleposervice_config_path))

    def _load_configuration(self):
        """
        Loads the configuration settings from the ePO service configuration file
        """
        config = ConfigParser()
        read_files = config.read(self._dxleposervice_config_path)
        if len(read_files) is not 1:
            raise Exception(
                "Error attempting to read service configuration file: {0}".format(
                    self._dxleposervice_config_path))

        # Determine the ePO servers in the configuration file
        epo_names_str = config.get(self.GENERAL_CONFIG_SECTION, self.GENERAL_EPO_NAMES_CONFIG_PROP)
        epo_names = epo_names_str.split(",")
        if len(epo_names_str.strip()) is 0 or len(epo_names) is 0:
            raise Exception("At least one ePO server must be defined in the service configuration file")

        # For each ePO specified, create an instance of the ePO object (used to communicate with
        # the ePO server via HTTP)
        for epo_name in epo_names:
            epo_name = epo_name.strip()
            host = config.get(epo_name, self.EPO_HOST_CONFIG_PROP)
            user = config.get(epo_name, self.EPO_USER_CONFIG_PROP)
            password = config.get(epo_name, self.EPO_PASSWORD_CONFIG_PROP)

            # Port (optional)
            port = self.DEFAULT_EPO_PORT
            try:
                port = config.get(epo_name, self.EPO_PORT_CONFIG_PROP)
            except NoOptionError:
                pass

            # Whether to verify the ePO server's certificate (optional)
            verify = self.DEFAULT_VERIFY_CERTIFICATE
            try:
                verify = config.getboolean(epo_name, self.EPO_VERIFY_CERTIFICATE)
            except NoOptionError:
                pass

            # CA Bundle
            if verify:
                try:
                    ca_bundle = config.get(epo_name, self.EPO_VERIFY_CERT_BUNDLE)
                    if ca_bundle:
                        ca_bundle = self._get_path(ca_bundle)
                        verify = ca_bundle

                        if not os.access(verify, os.R_OK):
                            raise Exception(
                                "Unable to access CA bundle file/dir ({0}): {1}".format(
                                    self.EPO_VERIFY_CERT_BUNDLE, verify))
                except NoOptionError:
                    pass

            # Create ePO wrapper
            epo = _Epo(name=epo_name, host=host, port=port, user=user,
                       password=password, verify=verify)

            # Unique identifier (optional, if not specified attempts to determine GUID)
            unique_id = None
            try:
                unique_id = config.get(epo_name, self.EPO_UNIQUE_ID_CONFIG_PROP)
            except NoOptionError:
                pass

            if unique_id is None:
                logger.info("Attempting to determine GUID for ePO server: {0} ...".format(epo_name))
                unique_id = epo.lookup_guid()
                logger.info("GUID '{0}' found for ePO server: {1}".format(unique_id, epo_name))

            # Create the request topic based on the ePO's unique identifier
            request_topic = self.DXL_REQUEST_FORMAT.format(unique_id)
            logger.info("Request topic '{0}' associated with ePO server: {1}".format(
                request_topic, epo_name))
            # Associate ePO wrapper instance with the request topic
            self._epo_by_topic[request_topic] = epo

        #
        # Load message pool settings
        #

        try:
            self._incoming_queue_size = config.getint(self.INCOMING_MESSAGE_POOL_CONFIG_SECTION,
                                                      self.INCOMING_MESSAGE_POOL_QUEUE_SIZE_CONFIG_PROP)
        except NoOptionError:
            pass

        try:
            self._incoming_thread_count = config.getint(self.INCOMING_MESSAGE_POOL_CONFIG_SECTION,
                                                        self.INCOMING_MESSAGE_POOL_THREAD_COUNT_CONFIG_PROP)
        except NoOptionError:
            pass

    def _dxl_connect(self):
        """
        Attempts to connect to the DXL fabric and register the ePO DXL service
        """

        # Connect to fabric
        config = DxlClientConfig.create_dxl_config_from_file(self._dxlclient_config_path)
        config.incoming_message_thread_pool_size = self._incoming_thread_count
        config.incoming_message_queue_size = self._incoming_queue_size
        logger.info("Incoming message configuration: queueSize={0}, threadCount={1}".format(
            config.incoming_message_queue_size, config.incoming_message_thread_pool_size))

        client = DxlClient(config)
        logger.info("Attempting to connect to DXL fabric ...")
        client.connect()
        logger.info("Connected to DXL fabric.")

        try:
            # Register service
            service = ServiceRegistrationInfo(client, self.DXL_SERVICE_TYPE)
            for request_topic in self._epo_by_topic:
                service.add_topic(str(request_topic), _EpoRequestCallback(client, self._epo_by_topic))

            logger.info("Registering service ...")
            client.register_service_sync(service, self.DXL_SERVICE_REGISTRATION_TIMEOUT)
            logger.info("Service registration succeeded.")
        except:
            client.destroy()
            raise

        self._dxl_client = client
        self._dxl_service = service

    def run(self):
        """
        Starts the ePO service. This will load the configuration files associated with the service,
        connect the DXL client to the fabric, and register the ePO DXL service with the fabric.
        """
        with self._lock:
            if self._running:
                raise Exception("The ePO service is already running")

            logger.info("Running service ...")
            self._validate_config_files()
            self._load_configuration()
            self._dxl_connect()
            self._running = True

    def destroy(self):
        """
        Destroys the ePO service. This will cause the ePO DXL service to be unregistered with the fabric
        and the DXL client to be disconnected.
        """
        with self._lock:
            if self._running and not self._destroyed:

                logger.info("Destroying service ...")
                if self._dxl_client is not None:

                    if self._dxl_service is not None:
                        logger.info("Unregistering service ...")
                        self._dxl_client.unregister_service_sync(
                            self._dxl_service, self.DXL_SERVICE_REGISTRATION_TIMEOUT)
                        logger.info("Service unregistration succeeded.")
                        self._dxl_service = None

                    self._dxl_client.destroy()
                    self._dxl_client = None
                self._destroyed = True

    def _get_path(self, in_path):
        """
        Returns an absolute path for a file specified in the configuration file (supports
        files relative to the configuration file).
        :param in_path: The specified path
        :return: An absolute path for a file specified in the configuration file
        """
        if not os.path.isfile(in_path) and not os.path.isabs(in_path):
            config_rel_path = os.path.join(self._config_dir, in_path)
            if os.path.isfile(config_rel_path):
                in_path = config_rel_path
        return in_path

class _EpoRequestCallback(RequestCallback):
    """
    Request callback used to handle incoming service requests
    """

    # UTF-8 encoding (used for encoding/decoding payloads)
    UTF_8 = "utf-8"

    # The key in the request used to specify the ePO command to invoke
    CMD_NAME_KEY = "command"
    # The key in the request used to specify the output format
    # (json, xml, verbose, terse). This is optional
    OUTPUT_KEY = "output"
    # The key used to specify the parameters for the ePO command
    PARAMS_KEY = "params"

    # The default output format
    DEFAULT_OUTPUT = "json"

    def __init__(self, client, epo_by_topic):
        """
        Constructs the callback

        :param client: The DXL client associated with the service
        :param epo_by_topic: The ePO server wrappers by associated request topics
        """
        super(_EpoRequestCallback, self).__init__()
        self._dxl_client = client
        self._epo_by_topic = epo_by_topic

    def on_request(self, request):
        """
        Invoked when a request is received

        :param request: The request that was received
        """
        try:
            # Build dictionary from the request payload
            req_dict = json.loads(request.payload.decode(encoding=self.UTF_8))

            # Determine the ePO command
            if self.CMD_NAME_KEY not in req_dict:
                raise Exception("A command name was not specified ('{0}')".format(self.CMD_NAME_KEY))
            command = req_dict[self.CMD_NAME_KEY]

            # Determine the request parameters
            req_params = {}
            if self.PARAMS_KEY in req_dict:
                req_params = req_dict[self.PARAMS_KEY]

            # Determine the output format
            output = self.DEFAULT_OUTPUT
            if self.OUTPUT_KEY in req_dict:
                output = req_dict[self.OUTPUT_KEY]

            # Get the ePO server to invoke the command on
            epo = self._epo_by_topic[request.destination_topic]

            # Execute the ePO Remote Command
            result = epo.execute(command, output, req_params)

            # Create the response, set payload, and deliver
            response = Response(request)
            response.payload = result
            self._dxl_client.send_response(response)

        except Exception as ex:
            logger.exception("Error while processing request")
            # Send error response
            self._dxl_client.send_response(
                ErrorResponse(request,
                              error_message=str(ex).encode(encoding=self.UTF_8)))
