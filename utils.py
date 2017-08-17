import configparser

__author__ = "Lucas Cristiano Calixto Dantas"
__copyright__ = "Copyright 2017, Lucas Cristiano Calixto Dantas"
__credits__ = ["Lucas Cristiano Calixto Dantas"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Lucas Cristiano Calixto Dantas"
__email__ = "lucascristiano27@gmail.com"
__status__ = "Development"


def merge_dicts(*dict_args):
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def read_config_file(config_file):
    # Load the default configuration file
    with open(config_file, 'r+') as f:
        sample_config = f.read()
    config = configparser.RawConfigParser(allow_no_value=True)
    config.read_string(sample_config)

    config_dict = {'fiware_service': config.get('service', 'fiware-service'),
                   'fiware_service_path': config.get('service', 'fiware-service-path'),
                   'cb_host': config.get('contextbroker', 'host'),
                   'cb_port': config.get('contextbroker', 'port'),
                   'idas_aaa': config.get('idas', 'OAuth'),
                   'idas_host': config.get('idas', 'host'),
                   'idas_admin_port': config.get('idas', 'adminport'),
                   'idas_ul20_port': config.get('idas', 'ul20port'),
                   'api_key': config.get('idas', 'apikey'),
                   'mosquitto_host': config.get('mosquitto', 'host'),
                   'mosquitto_port': config.get('mosquitto', 'port'),
                   'sth_host': config.get('sthcomet', 'host'),
                   'sth_port': config.get('sthcomet', 'port'),
                   'cygnus_host': config.get('cygnus', 'host'),
                   'cygnus_notification_host': config.get('cygnus', 'notification_host'),
                   'cygnus_port': config.get('cygnus', 'port'),
                   'perseo_host': config.get('perseo', 'host'),
                   'perseo_port': config.get('perseo', 'port')
                   }

    if config_dict['idas_aaa'] == "yes":
        config_dict['token'] = config.get('user', 'token')
        config_dict['token_show'] = config_dict['token'][1:5] + "*" * 70 + config_dict['token'][-5:]
    else:
        config_dict['token'] = "NULL"
        config_dict['token_show'] = "NULL"

    config_dict['host_id'] = config.get('local', 'host_id')

    f.close()

    return config_dict