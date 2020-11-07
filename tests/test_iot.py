from os.path import dirname, realpath, join

from fiotclient.iot import FiwareIotClient
from . import TestCommonMethods


class TestIotMethods(TestCommonMethods):

    files_dir_path = join(dirname(realpath(__file__)), 'files')

    def test_config_file_init_inherited_params(self):
        iot_client = FiwareIotClient.from_config_file(self._build_file_path('config.dummy.json'))

        self.assertEqual(iot_client.fiware_config.service, 'service_name')
        self.assertEqual(iot_client.fiware_config.service_path, '/service_path')

        self.assertEqual(iot_client.fiware_config.cb_host, 'context_broker_address')
        self.assertEqual(iot_client.fiware_config.cb_port, 1)
        # TODO Check OAuth param

        # TODO Check these verifications
        self.assertEqual(iot_client.fiware_config.iota_aaa, False)
        # self.assertEqual(iot_client.token, '')
        # self.assertEqual(iot_client.expires_at, '')

        self.assertEqual(iot_client.fiware_config.host_id, 'b4:b6:30')

    def test_config_file_init_specific_params(self):
        iot_client = FiwareIotClient.from_config_file(self._build_file_path('config.dummy.json'))

        self.assertEqual(iot_client.fiware_config.iota_host, 'iota_address')
        self.assertEqual(iot_client.fiware_config.iota_north_port, 2)
        self.assertEqual(iot_client.fiware_config.iota_protocol_port, 3)
        # check IOTA auth attr
        self.assertEqual(iot_client.fiware_config.api_key, '1a2b3c4d5e6f')

        self.assertEqual(iot_client.fiware_config.mqtt_broker_host, 'mqtt_broker_address')
        self.assertEqual(iot_client.fiware_config.mqtt_broker_port, 6)

        # TODO MQTT optional

        # TODO Check local SO

    def test_register_device(self):
        pass  # TODO Implement

    def test_register_device_from_file(self):
        response = self.iot_client.register_device_from_file(self._build_file_path('LED.json'), 'LED_001', 'TEST_LED')
        self.assertEqual(response['status_code'], 201)

        response = self.iot_client.get_device_by_id('LED_001')
        self.assertEqual(response['status_code'], 200)
        data = response['response']

        expected_device_data = {
            'device_id': 'LED_001',
            'entity_name': 'TEST_LED',
            'entity_type': 'thing',
            'transport': 'MQTT',
            'attributes': [{
                'object_id': 's',
                'name': 'state',
                'type': 'int'
            }],
            'lazy': [],
            'commands': [{
                'object_id': 'change_state',
                'name': 'change_state',
                'type': 'command'
            }],
            'static_attributes': [{
                'name': 'device_id',
                'type': 'string',
                'value': 'LED_001'}]
        }
        self._assert_device_data(data, expected_device_data)

        response = self.context_client.get_entity_by_id('TEST_LED', 'thing')
        self.assertEqual(response['status_code'], 200)
        data = response['response']

        expected_entity_data = {
            'id': 'TEST_LED',
            'type': 'thing',
            'change_state_info': {
                'type': 'commandResult',
                'value': ' '
            },
            'change_state_status': {
                'type': 'commandStatus',
                'value': 'UNKNOWN'
            },
            'state': {
                'type': 'int',
                'value': ' '
            },
            'device_id': {
                'type': 'string',
                'value': 'LED_001'
            }
        }
        self._assert_device_entity_data(data, expected_entity_data)

    def test_update_device(self):
        pass  # TODO Implement

    def test_remove_device(self):
        response = self.iot_client.register_device_from_file(self._build_file_path('LED.json'), 'LED_001', 'TEST_LED')
        self.assertEqual(response['status_code'], 201)

        response = self.iot_client.remove_device('LED_001')
        self.assertEqual(response['status_code'], 204)

        response = self.iot_client.get_device_by_id('LED_001')
        self.assertEqual(response['status_code'], 404)

    def test_get_device_by_id(self):
        pass  # TODO Implement

    def test_list_devices(self):
        pass  # TODO Implement

    def test_send_observation(self):
        pass  # TODO Implement

    def test_send_command(self):
        response = self.iot_client.register_device_from_file(self._build_file_path('LED.json'), 'LED_001', 'TEST_LED')
        self.assertEqual(response['status_code'], 201)

        response = self.context_client.get_entity_by_id('TEST_LED', 'thing')
        self.assertEqual(response['status_code'], 200)
        data = response['response']

        expected_entity_data = {
            'id': 'TEST_LED',
            'type': 'thing',
            'change_state_info': {
                'type': 'commandResult',
                'value': ' '
            },
            'change_state_status': {
                'type': 'commandStatus',
                'value': 'UNKNOWN'
            },
            'state': {
                'type': 'int',
                'value': ' '
            },
            'device_id': {
                'type': 'string',
                'value': 'LED_001'
            }
        }
        self._assert_device_entity_data(data, expected_entity_data)

        response = self.iot_client.send_command('TEST_LED', 'LED_001', 'change_state', {'state': 'ON'})
        self.assertEqual(response['status_code'], 200)

        response = self.context_client.get_entity_by_id('TEST_LED', 'thing')
        self.assertEqual(response['status_code'], 200)
        data = response['response']

        expected_entity_data = {
            'id': 'TEST_LED',
            'type': 'thing',
            'change_state_info': {
                'type': 'commandResult',
                'value': ' '
            },
            'change_state_status': {
                'type': 'commandStatus',
                'value': 'PENDING'
            },
            'state': {
                'type': 'int',
                'value': ' '
            },
            'device_id': {
                'type': 'string',
                'value': 'LED_001'
            }
        }
        self._assert_device_entity_data(data, expected_entity_data)

    def test_get_pooling_commands(self):
        pass  # TODO Implement

    def test_join_group_measurements(self):
        pass  # TODO Implement

    def test_create_ul_payload_from_measurements(self):
        pass  # TODO Implement

    def test_create_service(self):
        pass  # TODO Implement

    def test_remove_service(self):
        pass  # TODO Implement

    def test_list_services(self):
        pass  # TODO Implement

    def _build_file_path(self, filename):
        return join(self.files_dir_path, filename)

    def _assert_device_entity_data(self, data, expected_data):
        self.assertEqual(data['id'], expected_data['id'])
        self.assertEqual(data['type'], expected_data['type'])
        self.assertEqual(data['change_state_info']['type'], expected_data['change_state_info']['type'])
        self.assertEqual(data['change_state_info']['value'], expected_data['change_state_info']['value'])
        self.assertEqual(data['change_state_status']['type'], expected_data['change_state_status']['type'])
        self.assertEqual(data['change_state_status']['value'], expected_data['change_state_status']['value'])
        self.assertEqual(data['device_id']['type'], expected_data['device_id']['type'])
        self.assertEqual(data['device_id']['value'], expected_data['device_id']['value'])
        self.assertEqual(data['state']['type'], expected_data['state']['type'])
        self.assertEqual(data['state']['value'], expected_data['state']['value'])

    def _assert_device_data(self, data, expected_data):
        self.assertEqual(data['device_id'], expected_data['device_id'])
        self.assertEqual(data['entity_name'], expected_data['entity_name'])
        self.assertEqual(data['entity_type'], expected_data['entity_type'])
        self.assertEqual(data['transport'], expected_data['transport'])

        self.assertEqual(len(data['attributes']), len(expected_data['attributes']))
        self.assertEqual(data['attributes'][0]['object_id'], expected_data['attributes'][0]['object_id'])
        self.assertEqual(data['attributes'][0]['name'], expected_data['attributes'][0]['name'],)
        self.assertEqual(data['attributes'][0]['type'], expected_data['attributes'][0]['type'])

        self.assertEqual(len(data['lazy']), len(expected_data['lazy']))

        self.assertEqual(len(data['commands']), len(expected_data['commands']))
        self.assertEqual(data['commands'][0]['object_id'], expected_data['commands'][0]['object_id'])
        self.assertEqual(data['commands'][0]['name'], expected_data['commands'][0]['name'])
        self.assertEqual(data['commands'][0]['type'], expected_data['commands'][0]['type'])

        self.assertEqual(len(data['static_attributes']), len(expected_data['static_attributes']))
        self.assertEqual(data['static_attributes'][0]['name'], expected_data['static_attributes'][0]['name'])
        self.assertEqual(data['static_attributes'][0]['type'], expected_data['static_attributes'][0]['type'])
        self.assertEqual(data['static_attributes'][0]['value'], expected_data['static_attributes'][0]['value'])
