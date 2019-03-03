import configparser
import sys

__author__ = "Lucas Cristiano Calixto Dantas"
__copyright__ = "Copyright 2017, Lucas Cristiano Calixto Dantas"
__credits__ = ["Lucas Cristiano Calixto Dantas"]
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Lucas Cristiano Calixto Dantas"
__email__ = "lucascristiano27@gmail.com"
__status__ = "Development"


def merge_dicts(*dict_args):
    """Merge two dicts into a single dictionary

    :param dict_args: The dicts to be merged
    :return: The resulting dictionary from the merge
    """

    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def read_config_file(config_file):
    """Load configuration file and creates a dict with the necessary attributes

    :param config_file: The file to be read
    :return: A dict with the attributes read from the file
    """
    with open(config_file, 'r+') as f:
        sample_config = f.read()
    config = configparser.RawConfigParser(allow_no_value=True)

    if sys.version_info[0] > 2:
        config.read_string(sample_config)
    else:
        reload(sys)
        sys.setdefaultencoding('utf8')
        config.read_string(unicode(sample_config))

    config_dict = {'fiware_service': config.get('service', 'fiware_service'),
                   'fiware_service_path': config.get('service', 'fiware_service_path'),
                   'cb_host': config.get('context_broker', 'host'),
                   'cb_port': config.getint('context_broker', 'port'),
                   'iota_aaa': config.get('iota', 'OAuth'),
                   'iota_host': config.get('iota', 'host'),
                   'iota_north_port': config.getint('iota', 'north_port'),
                   'iota_protocol_port': config.getint('iota', 'protocol_port'),
                   'api_key': config.get('iota', 'api_key'),
                   'mqtt_broker_host': config.get('mqtt_broker', 'host'),
                   'mqtt_broker_port': config.getint('mqtt_broker', 'port'),
                   'sth_host': config.get('sth_comet', 'host'),
                   'sth_port': config.getint('sth_comet', 'port'),
                   'cygnus_host': config.get('cygnus', 'host'),
                   'cygnus_notification_host': config.get('cygnus', 'notification_host'),
                   'cygnus_port': config.getint('cygnus', 'port'),
                   'perseo_host': config.get('perseo', 'host'),
                   'perseo_port': config.getint('perseo', 'port')
                   }

    if config_dict['iota_aaa'] == "yes":
        config_dict['token'] = config.get('user', 'token')
        config_dict['token_show'] = config_dict['token'][1:5] + "*" * 70 + config_dict['token'][-5:]
    else:
        config_dict['token'] = "NULL"
        config_dict['token_show'] = "NULL"

    config_dict['host_id'] = config.get('local', 'host_id')

    f.close()

    return config_dict
