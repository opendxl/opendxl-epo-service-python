import json
import os
import re
import sys

from tempfile import NamedTemporaryFile
from mock import patch
from dxleposervice import EpoService
from tests.mock_epohttpserver import MockServerRunner
from tests.test_base import BaseClientTest
from tests.test_service import create_eposervice_configfile
from tests.test_value_constants import *

if sys.version_info[0] > 2:
    import builtins  # pylint: disable=import-error, unused-import
    from urllib.parse import quote_plus  # pylint: disable=no-name-in-module, import-error, unused-import
else:
    import __builtin__  # pylint: disable=import-error

    builtins = __builtin__  # pylint: disable=invalid-name
    from urllib import quote_plus  # pylint: disable=no-name-in-module, ungrouped-imports


def expected_print_output(detail):
    json_string = json.dumps(
        detail,
        sort_keys=True,
        separators=(".*", ": ")
    )

    return re.sub(
        r"(\.\*)+",
        ".*",
        re.sub(
            r"[{[\]}]",
            ".*",
            json_string
        )
    )


class StringContains(object):
    def __init__(self, pattern):
        self.pattern = pattern

    def __eq__(self, other):
        return self.pattern in other


class StringDoesNotContain(object):
    def __init__(self, pattern):
        self.pattern = pattern

    def __eq__(self, other):
        return not self.pattern in other


class StringMatchesRegEx(object):
    def __init__(self, pattern):
        self.pattern = pattern

    def __eq__(self, other):
        return re.match(self.pattern, other, re.DOTALL)


class StringDoesNotMatchRegEx(object):
    def __init__(self, pattern):
        self.pattern = pattern

    def __eq__(self, other):
        return not re.match(self.pattern, other)


def run_sample(sample_file):
    with open(sample_file) as f, \
            patch.object(builtins, 'print') as mock_print:
        sample_globals = {"__file__": sample_file}
        exec(f.read(), sample_globals)  # pylint: disable=exec-used
    return mock_print


class TempSampleFile(object):

    @property
    def temp_file(self):
        return self._temp_file

    def __init__(self, sample_filename):
        self._temp_file = NamedTemporaryFile(
            mode="w+",
            dir=os.path.dirname(sample_filename),
            delete=False)
        self._temp_file.close()
        os.chmod(self._temp_file.name, 0o777)
        self.base_filename = sample_filename
        self.write_file_line()

    def write_file_line(self, target=None, replacement=None):
        with open(self.base_filename, 'r') as base_file:
            with open(self._temp_file.name, 'w+') as new_sample_file:

                for line in base_file:
                    if target != None and replacement != None:
                        if line.startswith(target):
                            line = replacement
                    new_sample_file.write(line)


    def __del__(self):
        self.temp_file.close()
        os.remove(self._temp_file.name)

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


class TestSamples(BaseClientTest):

    SAMPLE_FOLDER = str(
        os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)
                )
            )
        )
    )+ "/sample"

    BASIC_FOLDER = SAMPLE_FOLDER + "/basic"

    def test_corehelp_example(self):
        # Modify sample file to include necessary sample data
        sample_filename = self.BASIC_FOLDER + "/basic_core_help_example.py"
        temp_sample_file = TempSampleFile(sample_filename)

        with BaseClientTest.create_client(max_retries=0) as dxl_client:
            with MockServerRunner() as server_list:
                dxl_client.connect()

                epo_service = configure_epo_service(dxl_client, server_list)

                epo_id = get_epo_id(epo_service)

                target_line = "EPO_UNIQUE_ID = "
                replacement_line = target_line + "\"" \
                                   + epo_id \
                                   + "\"\n"
                temp_sample_file.write_file_line(target_line, replacement_line)

                mock_print = run_sample(temp_sample_file.temp_file.name)

                mock_print.assert_any_call(
                    StringContains(HELP_CMD_RESPONSE_PAYLOAD)
                )

                mock_print.assert_any_call(
                    StringDoesNotContain("Error")
                )

                dxl_client.disconnect()


    def test_systemfind_example(self):
       # Modify sample file to include necessary sample data
        sample_filename = self.BASIC_FOLDER + "/basic_system_find_example.py"
        temp_sample_file = TempSampleFile(sample_filename)

        with BaseClientTest.create_client(max_retries=0) as dxl_client:
            with MockServerRunner() as server_list:
                dxl_client.connect()

                epo_service = configure_epo_service(dxl_client, server_list)

                epo_id = get_epo_id(epo_service)

                target_line = "EPO_UNIQUE_ID = "
                replacement_line = target_line + "\"" \
                                   + epo_id \
                                   + "\"\n"
                temp_sample_file.write_file_line(target_line, replacement_line)

                mock_print = run_sample(temp_sample_file.temp_file.name)

                mock_print.assert_any_call(
                    StringMatchesRegEx(
                        expected_print_output(SYSTEM_FIND_PAYLOAD)
                    )
                )

                mock_print.assert_any_call(
                    StringDoesNotContain("Error")
                )

                dxl_client.disconnect()
