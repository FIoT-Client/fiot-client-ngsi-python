from fiotclient.context import FiwareContextClient
from . import TestCommonMethods


class TestContextMethods(TestCommonMethods):

    def test_config_file_init_inherited_params(self):
        context_client = FiwareContextClient.from_config_file(self._build_file_path('config.dummy.json'))

        self.assertEqual(context_client.fiware_config.service, 'service_name')
        self.assertEqual(context_client.fiware_config.service_path, '/service_path')

        self.assertEqual(context_client.fiware_config.cb_host, 'context_broker_address')
        self.assertEqual(context_client.fiware_config.cb_port, 1)
        # TODO Check OAuth param

        # TODO Check these verifications
        self.assertEqual(context_client.fiware_config.iota_aaa, False)
        # self.assertEqual(context_client.token, '')
        # self.assertEqual(context_client.expires_at, '')

        self.assertEqual(context_client.fiware_config.host_id, 'b4:b6:30')

    def test_config_file_init_specific_params(self):
        context_client = FiwareContextClient.from_config_file(self._build_file_path('config.dummy.json'))

        self.assertEqual(context_client.fiware_config.sth_host, 'sth_comet_address')
        self.assertEqual(context_client.fiware_config.sth_port, 4)

        self.assertEqual(context_client.fiware_config.cygnus_host, 'cygnus_address')
        self.assertEqual(context_client.fiware_config.cygnus_notification_host, 'cygnus_notification_host_address')
        self.assertEqual(context_client.fiware_config.cygnus_port, 5)

        self.assertEqual(context_client.fiware_config.perseo_host, 'perseo_address')
        self.assertEqual(context_client.fiware_config.perseo_port, 7)

        # TODO MQTT optional

        # TODO Check local SO

    def test_create_entity(self):
        entity_schema = """{
            "id": "[ENTITY_ID]",
            "type": "[ENTITY_TYPE]",
            "temperature": {
                "value": 23,
                "type": "Float"
            },
            "pressure": {
                "value": 720,
                "type": "Integer"
            }
        }"""

        response = self.context_client.create_entity(entity_schema, 'Room', 'ROOM_001')
        self.assertEqual(response['status_code'], 201)

        response = self.context_client.get_entity_by_id('ROOM_001', 'Room')
        self.assertEqual(response['status_code'], 200)

        data = response['response']

        expected_entity_data = {
            'id': 'ROOM_001',
            'type': 'Room',
            'pressure': {
                'type': 'Integer',
                'value': 720
            },
            'temperature': {
                'type': 'Float',
                'value': 23
            }
        }
        self._assert_entity_data(data, expected_entity_data)

    def test_create_entity_from_file(self):
        response = self.context_client.create_entity_from_file(self._build_file_path('ROOM.json'), 'Room', 'ROOM_001')
        self.assertEqual(response['status_code'], 201)

        response = self.context_client.get_entity_by_id('ROOM_001', 'Room')
        self.assertEqual(response['status_code'], 200)

        data = response['response']

        expected_entity_data = {
            'id': 'ROOM_001',
            'type': 'Room',
            'pressure': {
                'type': 'Integer',
                'value': 720
            },
            'temperature': {
                'type': 'Float',
                'value': 23
            }
        }
        self._assert_entity_data(data, expected_entity_data)

    def test_get_entities(self):
        entities_ids = ['ROOM_001', 'ROOM_002', 'ROOM_003']
        for entity_id in entities_ids:
            self.context_client.create_entity_from_file(self._build_file_path('ROOM.json'), 'Room', entity_id)

        response = self.context_client.get_entities()

        self.assertEqual(response['status_code'], 200)

        data = response['response']
        self.assertEqual(len(data), 3)

        for entity in data:
            self.assertIn(entity['id'], entities_ids)
            self.assertEqual(entity['type'], 'Room')

    def test_get_nonexistent_entity(self):
        response = self.context_client.get_entity_by_id('NON_EXIST', 'NonexistentType')
        self.assertEqual(response['status_code'], 404)

    def test_get_entities_by_nonexistent_type(self):
        response = self.context_client.get_entities_by_type('NonexistentType')
        self.assertEqual(response['status_code'], 200)

        data = response['response']
        self.assertEqual(len(data), 0)

    def test_get_entities_by_type(self):
        rooms_entities_ids = ['ROOM_001', 'ROOM_002', 'ROOM_003']
        cars_entities_ids = ['CAR_001', 'CAR_002']

        for entity_id in rooms_entities_ids:
            self.context_client.create_entity_from_file(self._build_file_path('ROOM.json'), 'Room', entity_id)

        for entity_id in cars_entities_ids:
            self.context_client.create_entity_from_file(self._build_file_path('CAR.json'), 'Car', entity_id)

        rooms_response = self.context_client.get_entities_by_type('Room')
        cars_response = self.context_client.get_entities_by_type('Car')

        self.assertEqual(rooms_response['status_code'], 200)
        self.assertEqual(cars_response['status_code'], 200)

        rooms_data = rooms_response['response']
        cars_data = cars_response['response']

        self.assertEqual(len(rooms_data), 3)
        self.assertEqual(len(cars_data), 2)

        for entity in rooms_data:
            self.assertIn(entity['id'], rooms_entities_ids)
            self.assertEqual(entity['type'], 'Room')
        for entity in cars_data:
            self.assertIn(entity['id'], cars_entities_ids)
            self.assertEqual(entity['type'], 'Car')

    def test_get_entities_by_type_param(self):
        rooms_entities_ids = ['ROOM_001', 'ROOM_002', 'ROOM_003']
        cars_entities_ids = ['CAR_001', 'CAR_002']

        for entity_id in rooms_entities_ids:
            self.context_client.create_entity_from_file(self._build_file_path('ROOM.json'), 'Room', entity_id)

        for entity_id in cars_entities_ids:
            self.context_client.create_entity_from_file(self._build_file_path('CAR.json'), 'Car', entity_id)

        rooms_response = self.context_client.get_entities(entity_type='Room')
        self.assertEqual(rooms_response['status_code'], 200)
        cars_response = self.context_client.get_entities(entity_type='Car')
        self.assertEqual(cars_response['status_code'], 200)

        rooms_data = rooms_response['response']
        cars_data = cars_response['response']

        self.assertEqual(len(rooms_data), 3)
        self.assertEqual(len(cars_data), 2)

        for entity in rooms_data:
            self.assertIn(entity['id'], rooms_entities_ids)
            self.assertEqual(entity['type'], 'Room')
        for entity in cars_data:
            self.assertIn(entity['id'], cars_entities_ids)
            self.assertEqual(entity['type'], 'Car')

    def test_update_entity(self):
        pass  # TODO Implement

    def test_update_entity_attribute_value(self):
        pass  # TODO Implement

    def _assert_entity_data(self, data, expected_data):
        self.assertEqual(data['id'], expected_data['id'])
        self.assertEqual(data['type'], expected_data['type'])
        self.assertEqual(data['pressure']['type'], expected_data['pressure']['type'])
        self.assertEqual(data['pressure']['value'], expected_data['pressure']['value'])
        self.assertEqual(data['temperature']['type'], expected_data['temperature']['type'])
        self.assertEqual(data['temperature']['value'], expected_data['temperature']['value'])