import requests, json
import configparser
import paho.mqtt.publish as publish


class FiwareIotClient:

    def __init__(self):
        config_file = "config.ini"

        # Load the configuration file
        with open(config_file,'r+') as f:
            sample_config = f.read()
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_string(sample_config)

        self.cb_host = config.get('contextbroker', 'host')
        self.cb_port = config.get('contextbroker', 'port')
        self.cb_fiware_service = config.get('contextbroker', 'fiware-service')
        self.cb_fiware_service_path = config.get('contextbroker', 'fiware-service-path')

        self.idas_host = config.get('idas', 'host')
        self.idas_admin_port = config.get('idas', 'adminport')
        self.idas_ul20_port = config.get('idas', 'ul20port')

        self.fiware_service = config.get('idas', 'fiware-service')
        self.fiware_service_path = config.get('idas', 'fiware-service-path')

        self.api_key = config.get('idas', 'apikey')

        self.idas_aaa = config.get('idas', 'OAuth')
        if self.idas_aaa == "yes":
           self.token = config.get('user', 'token')
           self.token_show = self.token[1:5] + "*"*70 + self.token[-5:]
        else:
          self.token = "NULL"
          self.token_show = "NULL"

        self.sth_host = config.get('sthcomet', 'host')
        self.sth_port = config.get('sthcomet', 'port')

        self.cygnus_host = config.get('cygnus', 'host')
        self.cygnus_notification_host = config.get('cygnus', 'notification_host')
        self.cygnus_port = config.get('cygnus', 'port')

        self.mosquitto_host = config.get('mosquitto', 'host')
        self.mosquitto_port = config.get('mosquitto', 'port')

        self.perseo_host = config.get('perseo', 'host')
        self.perseo_port = config.get('perseo', 'port')

        self.host_id = config.get('local', 'host_id')
        f.close()

    def _send_request(self, url, headers, payload, method, format_json_response=False):
        print("* Asking to ", url)
        print("* Headers: ")
        print(json.dumps(headers, indent=4))

        if not isinstance(payload, str):
            str_payload = json.dumps(payload, indent=4)
        else:
            str_payload = payload

        if str_payload != '':
            print("* Sending PAYLOAD: ")
            print(str_payload)
            print()
            print("...")

        if method == 'GET':
            r = requests.get(url, data=str_payload, headers=headers)
        elif method == 'POST':
            r = requests.post(url, data=str_payload, headers=headers)
        elif method == 'PUT':
            r = requests.put(url, data=str_payload, headers=headers)
        elif method == 'PUT':
            r = requests.delete(url, data=str_payload, headers=headers)
        else:
            print("Unsupported method '{}'. Select one of 'GET', 'POST', 'PUT' and 'DELETE'.".format(method))
            return

        print()
        print("* Status Code: ", str(r.status_code))
        print("* Response: ")

        if format_json_response:
            print(json.dumps(json.loads(r.text), indent=4))
        else:
            print(r.text)

        print()

    def get_token(self):
        import getpass

        print("===== GENERATING self.token =====")

        tokens_url = "http://cloud.lab.fi-ware.org:4730/v2.0/tokens"

        print()
        print("Now you will be prompted for your user/password within FIWARE Lab Oauth2.0 Authentication system")
        print("If you didn't go and register first at http://cloud.fiware.org")
        print()

        user = input("FIWARE Lab Username: ")
        password = getpass.getpass("FIWARE Lab Password: ")

        payload = {
            "auth": {
                "passwordCredentials": {
                    "username": str(user),
                    "password": str(password)
                }
            }
        }

        headers =  { 'Content-Type': 'application/json' }
        url = tokens_url

        resp = requests.post(url, data=json.dumps(payload), headers=headers)
        print()
        self.token = resp.json()["access"]["token"]["id"]
        self.token_show = self.token[1:5] + "*"*70 + self.token[-5:]
        self.expires = resp.json()["access"]["token"]["expires"]

        print("FIWARE Oauth2.0 Token: ", self.token)
        print()
        print("Token expires: ", self.expires)
        print()

    def create_service(self):
        print("===== CREATING SERVICE =====")

        url = "http://{}:{}/iot/services".format(self.idas_host, self.idas_admin_port)

        headers = { 'content-type': 'application/json',
                    'X-Auth-Token' : self.token,
                    'Fiware-Service' : self.fiware_service,
                    'Fiware-ServicePath' : self.fiware_service_path }

        payload = { "services": [{
                        "protocol": ["IoTA-UL"],
                        "apikey": str(self.api_key),
                        "token": "token2",
                        "cbroker": "http://{}:{}".format(self.cb_host, self.cb_port),
                        "entity_type": "thing",
                        "resource": "/iot/d"
                    }]
                 }

        self._send_request(url, headers, payload, 'POST')

    def list_devices(self):
        print("===== Listing devices =====")

        url = "http://{}:{}/iot/devices".format(self.idas_host, self.idas_admin_port)

        headers = { 'Content-Type': 'application/json',
                    'X-Auth-Token' : self.token,
                    'Fiware-Service' : self.fiware_service,
                    'Fiware-ServicePath' : self.fiware_service_path }

        payload = ''

        self._send_request(url, headers, payload, 'GET', format_json_response=True)

    def register_device(self, device_file_path, device_id, entity_id, device_ip='', device_port='', protocol='IoTA-UL'):
        print("===== REGISTERING DEVICE =====")

        url = "http://{}:{}/iot/devices?protocol={}".format(self.idas_host, self.idas_admin_port, protocol)

        headers = { 'Content-Type': 'application/json',
                    'X-Auth-Token' : self.token,
                    'Fiware-Service' : self.fiware_service,
                    'Fiware-ServicePath' : self.fiware_service_path }

        print("* opening: " + device_file_path)
        with open(device_file_path) as json_device_file:
            payload = json.load(json_device_file)

        json_str = json.dumps(payload)
        json_str = json_str.replace('[DEVICE_ID]', str(device_id)) \
                           .replace('[ENTITY_ID]', str(entity_id))

        if '"endpoint"' in json_str:
            json_str = json_str.replace('[DEVICE_IP]', str(device_ip)) \
                               .replace('[PORT]', str(device_port))

        payload = json.loads(json_str)

        self._send_request(url, headers, payload, 'POST', format_json_response=True)

    def send_observation(self, device_id, measurements, protocol='mqtt'):
        print("===== SENDING OBSERVATION =====")

        payload = '#'.join(['%s|%s' % (str(key), str(value)) for (key, value) in measurements.items()])

        if protocol == 'mqtt':
            print("* Transport: MQTT")
            topic = "/{}/{}/attrs".format(self.api_key, device_id)

            print("* Publishing to ", self.idas_host)
            print("* Topic: ", topic)
            print("* Sending PAYLOAD: ")
            print(payload)
            print()
            print("...")

            publish.single(topic, payload, hostname=self.mosquitto_host)
            print("* OK ")

        else:
            print("* Transport: UL-HTTP")
            url = "http://{}:{}/iot/d?k={}&i={}".format(self.idas_host, self.idas_ul20_port, self.api_key, device_id)

            headers = { 'Content-Type': 'text/plain',
                        'X-Auth-Token' : self.token,
                        'Fiware-Service' : self.fiware_service,
                        'Fiware-ServicePath' : self.fiware_service_path }

            self._send_request(url, headers, payload, 'POST')

    def get_entity_by_id(self, id):
        print("===== GETTING ENTITY BY ID '{}'=====".format(id))

        url = "http://{}:{}/v2/entities/{}/attrs?type=thing".format(self.cb_host, self.cb_port, id)

        headers = { 'X-Auth-Token' : self.token,
                    'Fiware-Service' : self.cb_fiware_service,
                    'Fiware-ServicePath' : self.cb_fiware_service_path }

        payload = ''

        self._send_request(url, headers, payload, 'GET', format_json_response=True)

    def get_entities_by_type(self, type):
        print("===== GETTING ENTITIES BY TYPE '{}'=====".format(type))

        from collections import Counter
        import re

        url = "http://{}:{}/v2/entities?type={}".format(self.cb_host, self.cb_port, type)

        headers = { 'X-Auth-Token' : self.token,
                    'Fiware-Service' : self.cb_fiware_service,
                    'Fiware-ServicePath' : self.cb_fiware_service_path }

        payload = ''

        print("* Asking to ", url)
        print("* Headers: ")
        print(json.dumps(headers, indent=4))
        print("* Sending PAYLOAD: ")
        print(json.dumps(payload, indent=4))
        print()
        print("...")
        r = requests.get(url, payload, headers=headers)
        print()
        print("* Status Code: ", str(r.status_code))
        print("* Response: ")

        entities = json.loads(r.text)

        print("***** Number of entities found: ", len(entities))
        print("**** List of entity IDs")
        for entity in entities:
            print(entity["id"])
        print()

        ASK = str(input("Do you want me to print all entities data? (yes/no)"))
        if ASK == "yes" or ASK == "y":
            print(json.dumps(entities, indent=4))

        print()

    def simulate_command(self, entity_id, device_id, command, params={}):
        # http://fiware-orion.readthedocs.io/en/latest/user/walkthrough_apiv1/index.html#ngsi10-standard-operations , at "Update context elements"
        print("===== SIMULATING COMMAND =====")
        url = "http://{}:{}/v1/updateContext".format(self.idas_host, self.idas_admin_port)

        headers = { 'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-Auth-Token' : self.token,
                    'Fiware-Service' : self.cb_fiware_service,
                    'Fiware-ServicePath' : self.cb_fiware_service_path }

        params = '|'.join(['%s' % (str(value)) for (key, value) in params.items()])
        # if params != '':
        #     params = '|' + params
        #
        # value = '{}@{}{}'.format(device_id, command, params)
        # print("Command value:", value)

        value = params

        payload = { "contextElements": [{
                        "type": "thing",
                        "isPattern": "false",
                        "id": entity_id,
                        "attributes": [{
                            "name": command,
                            "type": "command",
                            "value": value
                        }]
                    }],
                    "updateAction": "UPDATE"
                 }

        self._send_request(url, headers, payload, 'POST', format_json_response=True)

    def get_pooling_commands(self, sensor_id):
        print("===== GETTING POOLING COMMANDS =====")

        url = "http://{}:{}/iot/d?k={}&i={}".format(self.idas_host, self.idas_ul20_port, self.api_key, sensor_id)

        payload = ''

        headers = { 'Content-Type': 'application/json',
                    'X-Auth-Token' : self.token,
                    'Fiware-Service' : self.fiware_service,
                    'Fiware-ServicePath' : self.fiware_service_path }

        self._send_request(url, headers, payload, 'GET')

    def subscribe_attributes_change(self, device_id, attributes, notification_url):
        print("===== SUBSCRIBING TO ATTRIBUTES '{}' CHANGE =====".format(attributes))

        url = "http://{}:{}/v1/subscribeContext".format(self.cb_host, self.cb_port)

        headers = { 'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Auth-Token' : self.token,
                    'Fiware-Service' : self.cb_fiware_service,
                    'Fiware-ServicePath' : self.cb_fiware_service_path }

        payload = { "entities": [{
                        "type": "thing",
                        "isPattern": "false",
                        "id": str(device_id)
                    }],
                    "attributes": attributes,
                    "notifyConditions": [{
                        "type": "ONCHANGE",
                        "condValues": attributes
                    }],
                    "reference": notification_url,
                    "duration": "P1Y",
                    "throttling": "PT1S"
                  }

        self._send_request(url, headers, payload, 'POST')

    def subscribe_cygnus(self, entity_id, attributes):
        print("===== SUBSCRIBING CYGNUS =====")

        notification_url = "http://{}:{}/notify".format(self.cygnus_notification_host, self.cygnus_port)
        self.subscribe_attributes_change(entity_id, attributes, notification_url)

    def subscribe_historical_data(self, entity_id, attributes):
        print("===== SUBSCRIBING TO HISTORICAL DATA =====")

        notification_url = "http://{}:{}/notify".format(self.sth_host, self.sth_port)
        self.subscribe_attributes_change(entity_id, attributes, notification_url)

    def get_device_historical_data(self, entity_id, attribute, items_number=10):
        print("===== GETTING DEVICE HISTORICAL DATA =====")

        url = "http://{}:{}/STH/v1/contextEntities/type/thing/id/{}/attributes/{}?lastN={}".format(self.sth_host, self.sth_port, entity_id, attribute, items_number)

        headers = {'Accept': 'application/json',
                   'X-Auth-Token': self.token,
                   'Fiware-Service': str(self.cb_fiware_service).lower(),
                   'Fiware-ServicePath': str(self.cb_fiware_service_path).lower()}

        payload = ''

        self._send_request(url, headers, payload, 'GET', format_json_response=True)

    def create_attribute_change_rule(self, attribute, attribute_type, condition, notification_url, action='post'):
        print("===== CREATE ATTRIBUTE CHANGE RULE =====")

        url = "http://{}:{}/rules".format(self.perseo_host, self.perseo_port)

        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   'X-Auth-Token': self.token,
                   'Fiware-Service': self.cb_fiware_service,
                   'Fiware-ServicePath': self.cb_fiware_service_path}

        payload = {
            "name": "{}-rule".format(attribute),
            "text": "select *,\"{}-rule\" as ruleName from pattern [every ev=iotEvent(cast(cast(ev.{}?,String),{}){})]".format(
                attribute, attribute, attribute_type, condition),
            "action": {
                "type": "",
                "template": "Alert! {0} is now ${{ev.{1}}}.".format(attribute, attribute),
                "parameters": {}
            }
        }

        if action == 'email':
            payload["action"]["type"] = "email"
            payload["action"]["parameters"] = {"to": "{}".format("lucascristiano27@gmail.com"),
                                               "from": "{}".format("lucas.calixto.dantas@gmail.com"),
                                               "subject": "Alert! High {} Detected".format(attribute.capitalize())}
        else:  # if action == 'post':
            payload["action"]["type"] = "post"
            payload["action"]["parameters"] = {"url": "{}".format(notification_url)}

        self._send_request(url, headers, payload, 'POST', format_json_response=True)
