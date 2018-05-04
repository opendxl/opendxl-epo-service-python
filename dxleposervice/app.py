from __future__ import absolute_import
import logging
import os
import json

from dxlbootstrap.app import Application
from dxlclient.service import ServiceRegistrationInfo
from dxlclient.callbacks import RequestCallback
from dxlclient.message import ErrorResponse, Response

from ._epo import _Epo

# Configure local logger
logger = logging.getLogger(__name__)


class EpoService(Application):
    """
    A DXL service that exposes the remote commands of one or more ePO servers to
    the DXL fabric. When a DXL request message is received, the remote command is invoked
    on the appropriate ePO server and its response is packaged and returned to the invoking
    client via a DXL response message.
    """

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

    def __init__(self, config_dir):
        """
        Constructor parameters:

        :param config_dir: The location of the configuration files for the
            application
        """
        super(EpoService, self).__init__(config_dir, "dxleposervice.config")

        self._epo_by_topic = {}
        self._dxl_service = None

    @property
    def client(self):
        """
        The DXL client used by the application to communicate with the DXL
        fabric
        """
        return self._dxl_client

    @property
    def config(self):
        """
        The application configuration (as read from the "dxleposervice.config" file)
        """
        return self._config

    def on_run(self):
        """
        Invoked when the application has started running.
        """
        logger.info("On 'run' callback.")

    @staticmethod
    def _get_option(config, section, option, default_value=None):
        return config.get(section, option) \
            if config.has_option(section, option) else default_value

    @staticmethod
    def _get_boolean_option(config, section, option, default_value=False):
        return config.getboolean(section, option) \
            if config.has_option(section, option) else default_value

    def on_load_configuration(self, config):
        """
        Invoked after the application-specific configuration has been loaded

        This callback provides the opportunity for the application to parse
        additional configuration properties.

        :param config: The application configuration
        """
        logger.info("On 'load configuration' callback.")

        # Determine the ePO servers in the configuration file
        epo_names_str = config.get(self.GENERAL_CONFIG_SECTION,
                                   self.GENERAL_EPO_NAMES_CONFIG_PROP)
        epo_names = epo_names_str.split(",")
        if len(epo_names_str.strip()) is 0 or len(epo_names) is 0:
            raise Exception(
                "At least one ePO server must be defined in the service configuration file")

        # For each ePO specified, create an instance of the ePO object (used to communicate with
        # the ePO server via HTTP)
        for epo_name in epo_names:
            epo_name = epo_name.strip()
            host = config.get(epo_name, self.EPO_HOST_CONFIG_PROP)
            user = config.get(epo_name, self.EPO_USER_CONFIG_PROP)
            password = config.get(epo_name, self.EPO_PASSWORD_CONFIG_PROP)

            # Port (optional)
            port = self._get_option(config, epo_name, self.EPO_PORT_CONFIG_PROP,
                                    self.DEFAULT_EPO_PORT)

            # Whether to verify the ePO server's certificate (optional)
            verify = self._get_boolean_option(config, epo_name,
                                              self.EPO_VERIFY_CERTIFICATE,
                                              self.DEFAULT_VERIFY_CERTIFICATE)

            # CA Bundle
            if verify:
                ca_bundle = self._get_option(config, epo_name,
                                             self.EPO_VERIFY_CERT_BUNDLE)
                if ca_bundle:
                    ca_bundle = self._get_path(ca_bundle)
                    verify = ca_bundle

                    if not os.access(verify, os.R_OK):
                        raise Exception(
                            "Unable to access CA bundle file/dir ({0}): {1}".format(
                                self.EPO_VERIFY_CERT_BUNDLE, verify))

            # Create ePO wrapper
            epo = _Epo(name=epo_name, host=host, port=port, user=user,
                       password=password, verify=verify)

            # Unique identifier (optional, if not specified attempts to determine GUID)
            unique_id = self._get_option(config, epo_name,
                                         self.EPO_UNIQUE_ID_CONFIG_PROP)

            if unique_id is None:
                logger.info(
                    "Attempting to determine GUID for ePO server: %s ...",
                    epo_name)
                unique_id = epo.lookup_guid()
                logger.info(
                    "GUID '%s' found for ePO server: %s", unique_id, epo_name)

            # Create the request topic based on the ePO's unique identifier
            request_topic = self.DXL_REQUEST_FORMAT.format(unique_id)
            logger.info(
                "Request topic '%s' associated with ePO server: %s",
                request_topic, epo_name)
            # Associate ePO wrapper instance with the request topic
            self._epo_by_topic[request_topic] = epo

    def on_dxl_connect(self):
        """
        Invoked after the client associated with the application has connected
        to the DXL fabric.
        """
        logger.info("On 'DXL connect' callback.")

    def on_register_services(self):
        """
        Invoked when services should be registered with the application
        """
        # Register service
        service = ServiceRegistrationInfo(self.client, self.DXL_SERVICE_TYPE)
        for request_topic in self._epo_by_topic:
            service.add_topic(str(request_topic),
                              _EpoRequestCallback(self.client,
                                                  self._epo_by_topic))

        logger.info("Registering service ...")
        self.client.register_service_sync(service,
                                          self.DXL_SERVICE_REGISTRATION_TIMEOUT)
        logger.info("Service registration succeeded.")

        self._dxl_service = service

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
                raise Exception(
                    "A command name was not specified ('{0}')".format(
                        self.CMD_NAME_KEY))
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
                              error_message=str(ex).encode(
                                  encoding=self.UTF_8)))
