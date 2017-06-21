import configparser
import json

import paho.mqtt.publish as publish
import requests

from common import SimpleClient


class FiwareIotClient(SimpleClient):

    def __init__(self, config_file):
        super(SimpleClient, self).__init__()

        # Load the default configuration file
        with open(config_file, 'r+') as f:
            sample_config = f.read()
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_string(sample_config)

        self.idas_host = config.get('idas', 'host')
        self.idas_admin_port = config.get('idas', 'adminport')
        self.idas_ul20_port = config.get('idas', 'ul20port')
        self.api_key = config.get('idas', 'apikey')

        self.mosquitto_host = config.get('mosquitto', 'host')
        self.mosquitto_port = config.get('mosquitto', 'port')

        f.close()

    def _send_request(self, url, payload, method, format_json_response=False, additional_headers={}):
        default_headers = {'X-Auth-Token': self.token,
                           'Fiware-Service': self.fiware_service,
                           'Fiware-ServicePath': self.fiware_service_path}

        headers = {**default_headers, **additional_headers}

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
        elif method == 'DELETE':
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

        tokens_url = "http://cloud.lab.fi-ware.org:4730/v2.0/tokens"  # TODO Change token generation URL

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

        headers = {'Content-Type': 'application/json'}
        url = tokens_url

        resp = requests.post(url, data=json.dumps(payload), headers=headers)
        print()
        self.token = resp.json()["access"]["token"]["id"]
        self.token_show = self.token[1:5] + "*" * 70 + self.token[-5:]
        self.expires = resp.json()["access"]["token"]["expires"]

        print("FIWARE OAuth2.0 Token: {}".format(self.token))
        print("Token expires: {}".format(self.expires))

    def create_service(self, service, service_path):
        print("===== CREATING SERVICE =====")

        url = "http://{}:{}/iot/services".format(self.idas_host, self.idas_admin_port)

        additional_headers = {'Content-Type': 'application/json',
                              'Fiware-Service': service,
                              'Fiware-ServicePath': service_path}

        payload = {"services": [{
            "protocol": ["IoTA-UL"],
            "apikey": str(self.api_key),
            "token": "token2",
            "cbroker": "http://{}:{}".format(self.cb_host, self.cb_port),
            "entity_type": "thing",
            "resource": "/iot/d"
        }]}

        self._send_request(url, payload, 'POST', additional_headers=additional_headers)

    def set_service(self, service, service_path):
        self.fiware_service = service
        self.fiware_service_path = service_path

    def list_devices(self):
        print("===== LISTING DEVICES =====")

        url = "http://{}:{}/iot/devices".format(self.idas_host, self.idas_admin_port)
        additional_headers = {'Content-Type': 'application/json'}
        payload = ''

        self._send_request(url, payload, 'GET', format_json_response=True, additional_headers=additional_headers)

    def register_device(self, device_file_path, device_id, entity_id, device_ip='', device_port='', protocol='IoTA-UL'):
        print("===== REGISTERING DEVICE =====")

        url = "http://{}:{}/iot/devices?protocol={}".format(self.idas_host, self.idas_admin_port, protocol)

        additional_headers = {'Content-Type': 'application/json'}

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

        self._send_request(url, payload, 'POST', format_json_response=True, additional_headers=additional_headers)

    @staticmethod
    def _join_group_measurements(group_measurements):
        return '|'.join(['%s|%s' % (str(key), str(value)) for (key, value) in group_measurements.items()])

    def send_observation(self, device_id, measurements, protocol='mqtt'):
        print("===== SENDING OBSERVATION =====")

        if isinstance(measurements, list):  # multiple measurement groups list
            groups_payload = []
            for measurement_group in measurements:
                group_payload = FiwareIotClient._join_group_measurements(measurement_group)
                groups_payload.append(group_payload)

            payload = '#'.join(groups_payload)

        else:  # single measurement group dict
            payload = FiwareIotClient._join_group_measurements(measurements)

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

        elif protocol == 'http':
            print("* Transport: UL-HTTP")
            url = "http://{}:{}/iot/d?k={}&i={}".format(self.idas_host, self.idas_ul20_port, self.api_key, device_id)
            additional_headers = {'Content-Type': 'text/plain'}

            self._send_request(url, payload, 'POST', additional_headers=additional_headers)

        else:
            print("Unknown transport protocol '{}'. Accepted values are 'mqtt' and 'http'".format(protocol))

    def simulate_command(self, entity_id, device_id, command, params={}):
        # http://fiware-orion.readthedocs.io/en/latest/user/walkthrough_apiv1/index.html#ngsi10-standard-operations
        # at "Update context elements"
        print("===== SIMULATING COMMAND =====")

        url = "http://{}:{}/v1/updateContext".format(self.idas_host, self.idas_admin_port)

        additional_headers = {'Content-Type': 'application/json',
                              'Accept': 'application/json'}

        params = '|'.join(['%s' % (str(value)) for (key, value) in params.items()])
        # if params != '':
        #     params = '|' + params
        #
        # value = '{}@{}{}'.format(device_id, command, params)
        # print("Command value:", value)

        value = params

        payload = {"contextElements": [
            {
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

        self._send_request(url, payload, 'POST', format_json_response=True, additional_headers=additional_headers)

    def get_pooling_commands(self, sensor_id):
        print("===== GETTING POOLING COMMANDS =====")

        url = "http://{}:{}/iot/d?k={}&i={}".format(self.idas_host, self.idas_ul20_port, self.api_key, sensor_id)
        payload = ''
        additional_headers = {'Content-Type': 'application/json'}

        self._send_request(url, payload, 'GET', additional_headers=additional_headers)
