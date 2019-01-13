import unittest
from os.path import dirname, realpath, join
from fiotclient.iot import FiwareIotClient


class TestContextMethods(unittest.TestCase):

    files_dir_path = join(dirname(realpath(__file__)), 'files')

    def _build_file_path(self, filename):
        return join(self.files_dir_path, filename)

    def test_create_service(self):
        pass  # TODO Implement

    def test_remove_service(self):
        pass  # TODO Implement

    def test_list_services(self):
        pass  # TODO Implement
