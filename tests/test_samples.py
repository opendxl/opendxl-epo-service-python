import threading
import subprocess

from tests.test_service import *

SAMPLE_FOLDER = str(os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
).replace("\\", "/")) + "/sample"

BASIC_FOLDER = SAMPLE_FOLDER + "/basic"

COMMON_PY_FILENAME = SAMPLE_FOLDER + "/common.py"
NEW_COMMON_PY_FILENAME = COMMON_PY_FILENAME + ".new"

CONFIG_FOLDER = str(os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"))
CONFIG_FILENAME = CONFIG_FOLDER + "/dxlclient.config"
NEW_CONFIG_FILENAME = CONFIG_FILENAME + ".new"
CA_FILENAME = CONFIG_FOLDER + "/ca-bundle.crt"
CERT_FILENAME = CONFIG_FOLDER + "/client.crt"
KEY_FILENAME = CONFIG_FOLDER + "/client.key"

def overwrite_file_line(filename, target, replacement):
    base_file = open(filename, 'r')
    new_file = open(filename + ".new", "w+")

    for line in base_file:
        if line.startswith(target):
            line = replacement
        new_file.write(line)

    base_file.close()
    new_file.close()

    os.remove(filename)
    os.rename(filename + ".new", filename)


def overwrite_common_py():
    target_line = "CONFIG_FILE = "
    replacement_line = target_line + "\"" + CONFIG_FILENAME + "\"\n"
    overwrite_file_line(COMMON_PY_FILENAME, target_line, replacement_line)


def overwrite_config_cert_locations():
    target_line = "BrokerCertChain = "
    replacement_line = target_line + "\"" + CA_FILENAME + "\"\n"
    overwrite_file_line(CONFIG_FILENAME, target_line, replacement_line)

    target_line = "CertFile = "
    replacement_line = target_line + "\"" + CERT_FILENAME + "\"\n"
    overwrite_file_line(CONFIG_FILENAME, target_line, replacement_line)

    target_line = "PrivateKey = "
    replacement_line = target_line + "\"" + KEY_FILENAME + "\"\n"
    overwrite_file_line(CONFIG_FILENAME, target_line, replacement_line)

def configure_epo_service(dxl_client, server_list):

    create_eposervice_configfile(
        config_file_name=EPO_SERVICE_CONFIG_FILENAME,
        server_list=server_list
    )

    epo_service = EpoService(TEST_FOLDER)
    epo_service._dxl_client = dxl_client

    epo_service._load_configuration()
    epo_service.on_register_services()

    return epo_service

def get_epo_id(epo_service):
    return str(epo_service._dxl_service.topics[0])\
        .replace('/mcafee/service/epo/remote/', '')

class SampleRunner(object):

    def __init__(self, cmd, target=''):
        self.cmd = cmd
        self.target_file = target
        self.process = None
        self.output = "Not started"


    def run(self, timeout):
        def target():
            self.process = subprocess.Popen(
                [self.cmd, self.target_file],
                stdout=subprocess.PIPE,
                #stderr=subprocess.PIPE,
            )
            self.output = self.process.communicate()[0]

        thread = threading.Thread(target=target)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()

        return self.output.decode('utf-8')

class TestCoreHelpSample(BaseEpoServerTest):

    def test_corehelp_example(self):
        # Modify common/config files to work with local ".\test" directory
        overwrite_common_py()
        overwrite_config_cert_locations()

        server_list = start_mock_epo_server(number_of_servers=1)

        with self.create_client(max_retries=0) as dxl_client:
            dxl_client.connect()

            epo_service = configure_epo_service(dxl_client, server_list)

            epo_id = get_epo_id(epo_service)

            # Modify sample file to include necessary sample data
            sample_filename = BASIC_FOLDER + "/basic_core_help_example.py"

            target_line = "EPO_UNIQUE_ID = "
            replacement_line = target_line + "\"" \
                               + epo_id \
                               + "\"\n"
            overwrite_file_line(sample_filename, target_line, replacement_line)

            sample_runner = SampleRunner(
                cmd="python",
                target=sample_filename
            )
            output = sample_runner.run(timeout=10)

            self.assertNotIn("Error", output)
            self.assertIn(
                HELP_CMD_RESPONSE_PAYLOAD,
                output.replace('\r', '')
            )

            dxl_client.disconnect()


class TestSystemFindSample(BaseEpoServerTest):

    def test_systemfind_example(self):
        # Modify common/config files to work with local ".\test" directory
        overwrite_common_py()
        overwrite_config_cert_locations()

        server_list = start_mock_epo_server(number_of_servers=1)

        with self.create_client(max_retries=0) as dxl_client:
            dxl_client.connect()



            epo_service = configure_epo_service(dxl_client, server_list)

            epo_id = get_epo_id(epo_service)

            # Modify sample file to include necessary sample data
            sample_filename = BASIC_FOLDER + "/basic_system_find_example.py"

            target_line = "EPO_UNIQUE_ID = "
            replacement_line = target_line + "\"" \
                               + epo_id \
                               + "\"\n"
            overwrite_file_line(sample_filename, target_line, replacement_line)

            sample_runner = SampleRunner(
                cmd="python",
                target=sample_filename
            )
            output = sample_runner.run(timeout=30)

            self.assertNotIn("Error", output)
            self.assertListEqual(
                SYSTEM_FIND_PAYLOAD,
                json.loads(''.join(output))
            )

            dxl_client.disconnect()
