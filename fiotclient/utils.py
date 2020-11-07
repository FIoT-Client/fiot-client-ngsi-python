import json

from .config import FiwareConfig


def merge_dicts(*dict_args):
    """Merge two dicts into a single dictionary

    :param dict_args: The dicts to be merged
    :return: The resulting dictionary from the merge
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def read_config_file(config_file_path) -> FiwareConfig:
    """Load configuration file and creates a dict with the necessary attributes

    :param config_file_path: The path of config file to be read
    :return: A dict with the attributes read from the file
    """
    with open(config_file_path, 'r+') as f:
        config_str = f.read()
    return parse_config_json(config_str)


def parse_config_json(config_json_str: str) -> FiwareConfig:
    config_dict = json.loads(config_json_str)
    return parse_config_dict(config_dict)


def parse_config_dict(config_dict: dict) -> FiwareConfig:
    return FiwareConfig(config_dict)
