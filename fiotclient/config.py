
class FiwareConfig:

    # TODO Check and notify mandatory parameters on input config dict

    def __init__(self, config_json: dict):
        self.service = config_json.get('fiwareService', '')
        self.service_path = config_json.get('fiwareServicePath', '')

        self.cb_host = config_json.get('contextBroker', {}).get('host', '')
        self.cb_port = config_json.get('contextBroker', {}).get('port', '')
        # TODO Include OAuth param

        self.iota_aaa = config_json.get('iota', {}).get('oauth', '')
        self.iota_host = config_json.get('iota', {}).get('host', '')
        self.iota_north_port = config_json.get('iota', {}).get('northPort', '')
        self.iota_protocol_port = config_json.get('iota', {}).get('protocolPort', '')
        self.api_key = config_json.get('iota', {}).get('apiKey', '')

        self.mqtt_broker_host = config_json.get('mqttBroker', {}).get('host', '')
        self.mqtt_broker_port = config_json.get('mqttBroker', {}).get('port', '')

        self.sth_host = config_json.get('sthComet', {}).get('host', '')
        self.sth_port = config_json.get('sthComet', {}).get('port', '')

        self.cygnus_host = config_json.get('cygnus', {}).get('host', '')
        self.cygnus_port = config_json.get('cygnus', {}).get('port', '')
        self.cygnus_notification_host = config_json.get('cygnus', {}).get('notificationHost', '')

        self.perseo_host = config_json.get('perseo', {}).get('host', '')
        self.perseo_port = config_json.get('perseo', {}).get('port', '')

        if config_json.get('iota', {}).get('aaa', ''):
            self.token = config_json.get('user', {}).get('token', '')
            self.token_show = self.token[1:5] + "*" * 70 + self.token[-5:]
        else:
            self.token = 'NULL'
            self.token_show = 'NULL'

        self.host_id = config_json.get('local', {}).get('hostId', '')
