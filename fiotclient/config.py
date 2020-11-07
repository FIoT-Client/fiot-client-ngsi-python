
class FiwareConfig:

    # TODO Check and notify mandatory parameters on input config dict

    def __init__(self, config_json: dict):
        self.service = config_json['fiwareService']
        self.service_path = config_json['fiwareServicePath']

        self.cb_host = config_json['contextBroker']['host']
        self.cb_port = config_json['contextBroker']['port']
        # TODO Include OAuth param

        self.iota_aaa = config_json['iota']['oauth']
        self.iota_host = config_json['iota']['host']
        self.iota_north_port = config_json['iota']['northPort']
        self.iota_protocol_port = config_json['iota']['protocolPort']
        self.api_key = config_json['iota']['apiKey']

        self.mqtt_broker_host = config_json['mqttBroker']['host']
        self.mqtt_broker_port = config_json['mqttBroker']['port']

        self.sth_host = config_json['sthComet']['host']
        self.sth_port = config_json['sthComet']['port']

        self.cygnus_host = config_json['cygnus']['host']
        self.cygnus_port = config_json['cygnus']['port']
        self.cygnus_notification_host = config_json['cygnus']['notificationHost']

        self.perseo_host = config_json['perseo']['host']
        self.perseo_port = config_json['perseo']['port']

        if config_json['iota']['aaa']:
            self.token = config_json['user']['token']
            self.token_show = self.token[1:5] + "*" * 70 + self.token[-5:]
        else:
            self.token = 'NULL'
            self.token_show = 'NULL'

        self.host_id = config_json['local']['hostId']

        self.fiware_service_path = config_json['fiwareServicePath']
