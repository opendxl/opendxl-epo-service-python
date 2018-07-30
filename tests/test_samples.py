from tests.mock_epohttpserver import MockServerRunner
from tests.test_base import *
from tests.test_service import init_config_eposervice
from tests.test_value_constants import *


def configure_epo_service(dxl_client, server_list):

    epo_service = init_config_eposervice(server_list)

    epo_service._dxl_client = dxl_client

    epo_service._load_configuration()
    epo_service.on_register_services()

    return epo_service

def get_epo_id(epo_service):
    return str(epo_service._dxl_service.topics[0])\
        .replace('/mcafee/service/epo/remote/', '')


class TestSamples(BaseClientTest):

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

                mock_print = BaseClientTest.run_sample(temp_sample_file.temp_file.name)

                mock_print.assert_any_call(
                    StringContains(HELP_CMD_RESPONSE_PAYLOAD)
                )

                mock_print.assert_any_call(
                    StringDoesNotContain("Error")
                )

                dxl_client.disconnect()

            os.remove(EPO_SERVICE_CONFIG_FILENAME)


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

                target_line = "SEARCH_TEXT = "
                replacement_line = target_line + "\"" \
                                   + SYSTEM_FIND_OSTYPE_LINUX \
                                   + "\"\n"
                temp_sample_file.write_file_line(target_line, replacement_line)

                mock_print = BaseClientTest.run_sample(temp_sample_file.temp_file.name)

                mock_print.assert_any_call(
                    StringMatchesRegEx(
                        BaseClientTest.expected_print_output(SYSTEM_FIND_PAYLOAD)
                    )
                )

                mock_print.assert_any_call(
                    StringDoesNotContain("Error")
                )

                dxl_client.disconnect()

            os.remove(EPO_SERVICE_CONFIG_FILENAME)
