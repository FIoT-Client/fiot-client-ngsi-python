import unittest
from fiotclient.context import FiwareContextClient

class TestContextMethods(unittest.TestCase):

    def test_config_file_init_inherited_params(self):
        context_client = FiwareContextClient('files/config.dummy.ini')

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
        context_client = FiwareContextClient('files/config.dummy.ini')

        self.assertEqual(context_client.sth_host, 'sthcomet_address')
        self.assertEqual(context_client.sth_port, 4)

        self.assertEqual(context_client.cygnus_host, 'cygnus_address')
        self.assertEqual(context_client.cygnus_notification_host, 'cygnus_notification_host_address')
        self.assertEqual(context_client.cygnus_port, 5)

        self.assertEqual(context_client.perseo_host, 'perseo_address')
        self.assertEqual(context_client.perseo_port, 7)

        # TODO Mqtt optional

        # TODO check local SO

    def assert_entity_data(self, data):
        self.assertEqual(data['id'], 'ROOM_001')
        self.assertEqual(data['type'], 'Room')
        self.assertEqual(data['pressure']['type'], 'Integer')
        self.assertEqual(data['pressure']['value'], 720)
        self.assertEqual(data['temperature']['type'], 'Float')
        self.assertEqual(data['temperature']['value'], 23)

    def test_create_entity(self):
        context_client = FiwareContextClient('files/config.ini')

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
        data = response['response']
        self.assert_entity_data(data)

    def test_create_entity_from_file(self):
        context_client = FiwareContextClient('files/config.ini')

        context_client.remove_entity('Room', 'ROOM_001')  # Delete entity with id if exists

        response = context_client.create_entity_from_file('files/ROOM.json', 'Room', 'ROOM_001')
        self.assertEqual(response['status_code'], 201)

        response = context_client.get_entity_by_id('ROOM_001', 'Room')
        self.assertEqual(response['status_code'], 200)
        data = response['response']
        self.assert_entity_data(data)


