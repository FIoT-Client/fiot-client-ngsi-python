import unittest
from os.path import dirname, realpath, join
from fiotclient.iot import FiwareIotClient


class TestContextMethods(unittest.TestCase):

    files_dir_path = join(dirname(realpath(__file__)), 'files')

    def _build_file_path(self, filename):
        return join(self.files_dir_path, filename)

    def test_config_file_init_inherited_params(self):
        iot_client = FiwareIotClient(self._build_file_path('config.dummy.ini'))

        self.assertEqual(iot_client.fiware_service, 'service_name')
        self.assertEqual(iot_client.fiware_service_path, '/service_path')

        self.assertEqual(iot_client.cb_host, 'contextbroker_address')
        self.assertEqual(iot_client.cb_port, 1)
        # TODO Check OAuth param

        # TODO Check these verifications
        self.assertEqual(iot_client.idas_aaa, 'no')
        # self.assertEqual(iot_client.token, '')
        # self.assertEqual(iot_client.expires_at, '')

        self.assertEqual(iot_client.host_id, 'b4:b6:30')

    def test_config_file_init_specific_params(self):
        iot_client = FiwareIotClient(self._build_file_path('config.dummy.ini'))

        self.assertEqual(iot_client.idas_host, 'idas_address')
        self.assertEqual(iot_client.idas_admin_port, 2)
        self.assertEqual(iot_client.idas_ul20_port, 3)
        # check IDAS auth attr
        self.assertEqual(iot_client.api_key, '1a2b3c4d5e6f')

        self.assertEqual(iot_client.mosquitto_host, 'mosquitto_address')
        self.assertEqual(iot_client.mosquitto_port, 6)

        # TODO MQTT optional

        # TODO Check local SO

    def test_create_service(self):
        pass  # TODO Implement

    def test_remove_service(self):
        pass  # TODO Implement

    def test_list_services(self):
        pass  # TODO Implement

    def test_register_device(self):
        pass  # TODO Implement

    def test_register_device_from_file(self):
        pass  # TODO Implement

    def test_update_device(self):
        pass  # TODO Implement

    def test_remove_device(self):
        pass  # TODO Implement

    def test_get_device_by_id(self):
        pass  # TODO Implement

    def test_list_devices(self):
        pass  # TODO Implement

    def test_send_observation(self):
        pass  # TODO Implement

    def test_send_command(self):
        pass  # TODO Implement

    def test_get_pooling_commands(self):
        pass  # TODO Implement

    def test_join_group_measurements(self):
        pass  # TODO Implement

    def test_create_ul_payload_from_measurements(self):
        pass  # TODO Implement
