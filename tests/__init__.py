import unittest
from os.path import dirname, realpath, join

from fiotclient.context import FiwareContextClient
from fiotclient.iot import FiwareIotClient


class TestCommonMethods(unittest.TestCase):

    files_dir_path = join(dirname(realpath(__file__)), 'files')

    def __init__(self, method_name):
        super().__init__(methodName=method_name)
        self.context_client = FiwareContextClient.from_config_file(TestCommonMethods._build_file_path('config.json'))
        self.iot_client = FiwareIotClient.from_config_file(TestCommonMethods._build_file_path('config.json'))

    def setUp(self):
        self._remove_all_entities()
        self._remove_all_devices()

    @classmethod
    def tearDownClass(cls):
        cls._remove_all_entities()
        cls._remove_all_devices()

    @staticmethod
    def _build_file_path(filename):
        return join(TestCommonMethods.files_dir_path, filename)

    @staticmethod
    def _remove_all_entities():
        context_client = FiwareContextClient.from_config_file(TestCommonMethods._build_file_path('config.json'))
        response = context_client.get_entities()
        data = response['response']

        for entity in data:
            context_client.remove_entity(entity['type'], entity['id'])

    @staticmethod
    def _remove_all_devices():
        iot_client = FiwareIotClient.from_config_file(TestCommonMethods._build_file_path('config.json'))
        context_client = FiwareContextClient.from_config_file(TestCommonMethods._build_file_path('config.json'))

        response = iot_client.list_devices()
        data = response['response']
        devices = data['devices']

        for device in devices:
            # Remove devices
            iot_client.remove_device(device['device_id'])

            # Remove entity associated to each device
            context_client.remove_entity('thing', device['entity_name'])
