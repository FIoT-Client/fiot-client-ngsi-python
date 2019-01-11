import unittest
from os.path import dirname, realpath, join
from fiotclient.context import FiwareContextClient


class TestContextMethods(unittest.TestCase):

    files_dir_path = join(dirname(realpath(__file__)), 'files')

    def _build_file_path(self, filename):
        return join(self.files_dir_path, filename)

    def test_config_file_init_inherited_params(self):
        context_client = FiwareContextClient(self._build_file_path('config.dummy.ini'))

        self.assertEqual(context_client.fiware_service, 'service_name')
        self.assertEqual(context_client.fiware_service_path, '/service_path')

        self.assertEqual(context_client.cb_host, 'contextbroker_address')
        self.assertEqual(context_client.cb_port, 1)
        # TODO Check OAuth param

        # TODO Check these verifications
        self.assertEqual(context_client.idas_aaa, 'no')
        # self.assertEqual(context_client.token, '')
        # self.assertEqual(context_client.expires_at, '')

        self.assertEqual(context_client.host_id, 'b4:b6:30')

    def test_config_file_init_specific_params(self):
        context_client = FiwareContextClient(self._build_file_path('config.dummy.ini'))

        self.assertEqual(context_client.sth_host, 'sthcomet_address')
        self.assertEqual(context_client.sth_port, 4)

        self.assertEqual(context_client.cygnus_host, 'cygnus_address')
        self.assertEqual(context_client.cygnus_notification_host, 'cygnus_notification_host_address')
        self.assertEqual(context_client.cygnus_port, 5)

        self.assertEqual(context_client.perseo_host, 'perseo_address')
        self.assertEqual(context_client.perseo_port, 7)

        # TODO MQTT optional

        # TODO Check local SO

    def assert_entity_data(self, data):
        self.assertEqual(data['id'], 'ROOM_001')
        self.assertEqual(data['type'], 'Room')
        self.assertEqual(data['pressure']['type'], 'Integer')
        self.assertEqual(data['pressure']['value'], 720)
        self.assertEqual(data['temperature']['type'], 'Float')
        self.assertEqual(data['temperature']['value'], 23)

    def test_create_entity(self):
        context_client = FiwareContextClient(self._build_file_path('config.ini'))

        context_client.remove_entity('Room', 'ROOM_001')  # Delete entity with id if exists

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

        response = context_client.create_entity(entity_schema, 'Room', 'ROOM_001')
        self.assertEqual(response['status_code'], 201)

        response = context_client.get_entity_by_id('ROOM_001', 'Room')
        self.assertEqual(response['status_code'], 200)

        # Delete created entity before running the asserts
        context_client.remove_entity('Room', 'ROOM_001')

        data = response['response']
        self.assert_entity_data(data)

    def test_create_entity_from_file(self):
        context_client = FiwareContextClient(self._build_file_path('config.ini'))

        context_client.remove_entity('Room', 'ROOM_001')  # Delete entity with id if exists

        response = context_client.create_entity_from_file(self._build_file_path('ROOM.json'), 'Room', 'ROOM_001')
        self.assertEqual(response['status_code'], 201)

        response = context_client.get_entity_by_id('ROOM_001', 'Room')
        self.assertEqual(response['status_code'], 200)

        # Delete created entity before running the asserts
        context_client.remove_entity('Room', 'ROOM_001')

        data = response['response']
        self.assert_entity_data(data)

    def test_get_entities(self):
        context_client = FiwareContextClient(join(self.files_dir_path, 'config.ini'))

        entities_ids = ['ROOM_001', 'ROOM_002', 'ROOM_003']

        # Delete entities with id if exists and recreate
        for entity_id in entities_ids:
            context_client.remove_entity('Room', entity_id)
            context_client.create_entity_from_file(self._build_file_path('ROOM.json'), 'Room', entity_id)

        response = context_client.get_entities()

        # Delete created entities before running the asserts
        for entity_id in entities_ids:
            context_client.remove_entity('Room', entity_id)

        self.assertEqual(response['status_code'], 200)

        data = response['response']
        self.assertEqual(len(data), 3)

        for entity in data:
            self.assertIn(entity['id'], entities_ids)
            self.assertEqual(entity['type'], 'Room')

    def test_get_nonexistent_entity(self):
        context_client = FiwareContextClient(join(self.files_dir_path, 'config.ini'))
        response = context_client.get_entity_by_id('NON_EXIST', 'NonexistentType')
        self.assertEqual(response['status_code'], 404)

    def test_get_entities_by_nonexistent_type(self):
        context_client = FiwareContextClient(join(self.files_dir_path, 'config.ini'))

        response = context_client.get_entities_by_type('NonexistentType')
        self.assertEqual(response['status_code'], 200)

        data = response['response']
        self.assertEqual(len(data), 0)

    def test_get_entities_by_type(self):
        context_client = FiwareContextClient(join(self.files_dir_path, 'config.ini'))

        rooms_entities_ids = ['ROOM_001', 'ROOM_002', 'ROOM_003']
        cars_entities_ids = ['CAR_001', 'CAR_002']

        # Delete entities with id if exists and recreate
        for entity_id in rooms_entities_ids:
            context_client.remove_entity('Room', entity_id)
            context_client.create_entity_from_file(self._build_file_path('ROOM.json'), 'Room', entity_id)

        for entity_id in cars_entities_ids:
            context_client.remove_entity('Car', entity_id)
            context_client.create_entity_from_file(self._build_file_path('CAR.json'), 'Car', entity_id)

        rooms_response = context_client.get_entities_by_type('Room')
        cars_response = context_client.get_entities_by_type('Car')

        # Delete created entities before running the asserts
        for entity_id in rooms_entities_ids:
            context_client.remove_entity('Room', entity_id)
        for entity_id in cars_entities_ids:
            context_client.remove_entity('Car', entity_id)

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
        context_client = FiwareContextClient(join(self.files_dir_path, 'config.ini'))

        rooms_entities_ids = ['ROOM_001', 'ROOM_002', 'ROOM_003']
        cars_entities_ids = ['CAR_001', 'CAR_002']

        # Delete entities with id if exists and recreate
        for entity_id in rooms_entities_ids:
            context_client.remove_entity('Room', entity_id)
            context_client.create_entity_from_file(self._build_file_path('ROOM.json'), 'Room', entity_id)

        for entity_id in cars_entities_ids:
            context_client.remove_entity('Car', entity_id)
            context_client.create_entity_from_file(self._build_file_path('CAR.json'), 'Car', entity_id)

        rooms_response = context_client.get_entities(entity_type='Room')
        cars_response = context_client.get_entities(entity_type='Car')

        # Delete created entities before running the asserts
        for entity_id in rooms_entities_ids:
            context_client.remove_entity('Room', entity_id)
        for entity_id in cars_entities_ids:
            context_client.remove_entity('Car', entity_id)

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

    def test_update_entity(self):
        pass  # TODO Implement

    def test_update_entity_attribute_value(self):
        pass  # TODO Implement
