import json
import logging

import paho.mqtt.publish as publish

import utils
from common import SimpleClient

__author__ = "Lucas Cristiano Calixto Dantas"
__copyright__ = "Copyright 2017, Lucas Cristiano Calixto Dantas"
__credits__ = ["Lucas Cristiano Calixto Dantas"]
__license__ = "GPL"
__version__ = "0.1.0"
__maintainer__ = "Lucas Cristiano Calixto Dantas"
__email__ = "lucascristiano27@gmail.com"
__status__ = "Development"


class FiwareIotClient(SimpleClient):

    def __init__(self, config_file):
        super().__init__(config_file)

        config_dict = utils.read_config_file(config_file)

        self.idas_host = config_dict['idas_host']
        self.idas_admin_port = config_dict['idas_admin_port']
        self.idas_ul20_port = config_dict['idas_ul20_port']
        self.api_key = config_dict['api_key']

        self.mosquitto_host = config_dict['mosquitto_host']
        self.mosquitto_port = config_dict['mosquitto_port']

    def create_service(self, service, service_path, api_key=None):
        logging.info("CREATING SERVICE")

        url = "http://{}:{}/iot/services".format(self.idas_host, self.idas_admin_port)

        additional_headers = {'Content-Type': 'application/json',
                              'Fiware-Service': service,
                              'Fiware-ServicePath': service_path}

        if api_key is not None:
            response = self._create_service(url, api_key, additional_headers)

        else:
            api_key = self.generate_api_key()

            created = False
            response = None

            while not created:
                response = self._create_service(url, api_key, additional_headers)

                if response['status_code'] == 201:
                    created = True
                else:
                    api_key = self.generate_api_key()

        response['api_key'] = api_key
        return response

    def _create_service(self, url, api_key, additional_headers):
        payload = {"services": [{
            "protocol": ["IoTA-UL"],  # TODO Remove hardcoded protocol
            "apikey": str(api_key),
            "token": "token2",
            "cbroker": "http://{}:{}".format(self.cb_host, self.cb_port),
            "entity_type": "thing",
            "resource": "/iot/d"
        }]}

        return self._send_request(url, payload, 'POST', additional_headers=additional_headers)

    def set_api_key(self, api_key):
        self.api_key = api_key

    def list_devices(self):
        logging.info("Listing devices")

        url = "http://{}:{}/iot/devices".format(self.idas_host, self.idas_admin_port)
        additional_headers = {'Content-Type': 'application/json'}
        payload = ''

        return self._send_request(url, payload, 'GET', additional_headers=additional_headers)

    def register_device(self, device_file_path, device_id, entity_id, device_ip='', device_port='', protocol='IoTA-UL'):
        logging.info("Registering device")

        url = "http://{}:{}/iot/devices?protocol={}".format(self.idas_host, self.idas_admin_port, protocol)

        additional_headers = {'Content-Type': 'application/json'}

        logging.info("Opening file '{}'".format(device_file_path))
        with open(device_file_path) as json_device_file:
            payload = json.load(json_device_file)

        json_str = json.dumps(payload)
        json_str = json_str.replace('[DEVICE_ID]', str(device_id)) \
                           .replace('[ENTITY_ID]', str(entity_id))

        if '"endpoint"' in json_str:
            json_str = json_str.replace('[DEVICE_IP]', str(device_ip)) \
                               .replace('[PORT]', str(device_port))

        payload = json.loads(json_str)

        return self._send_request(url, payload, 'POST', additional_headers=additional_headers)

    @staticmethod
    def _join_group_measurements(group_measurements):
        return '|'.join(['%s|%s' % (str(key), str(value)) for (key, value) in group_measurements.items()])

    def send_observation(self, device_id, measurements, protocol='MQTT'):
        logging.info("Sending observation")

        if isinstance(measurements, list):
            # multiple measurement groups list
            groups_payload = []
            for measurement_group in measurements:
                group_payload = FiwareIotClient._join_group_measurements(measurement_group)
                groups_payload.append(group_payload)

            payload = '#'.join(groups_payload)

        else:
            # single measurement group dict
            payload = FiwareIotClient._join_group_measurements(measurements)

        if protocol == 'MQTT':
            logging.info("Transport protocol: MQTT")
            topic = "/{}/{}/attrs".format(self.api_key, device_id)

            logging.info("Publishing to {} on topic {}".format(self.idas_host, topic))
            logging.info("Sending payload: ")
            logging.info(payload)

            publish.single(topic, payload, hostname=self.mosquitto_host)
            logging.info("Message sent")
            return {'result': 'OK'}

        elif protocol == 'HTTP':
            logging.info("Transport protocol: UL-HTTP")
            url = "http://{}:{}/iot/d?k={}&i={}".format(self.idas_host, self.idas_ul20_port, self.api_key, device_id)
            additional_headers = {'Content-Type': 'text/plain'}

            self._send_request(url, payload, 'POST', additional_headers=additional_headers)
            return {'result': 'OK'}

        else:
            logging.error("Unknown transport protocol '{}'".format(protocol))
            error_msg = "Unknown transport protocol. Accepted values are 'MQTT' and 'HTTP'"
            return {'error': error_msg}

    def send_command(self, entity_id, device_id, command, params=None):
        # http://fiware-orion.readthedocs.io/en/latest/user/walkthrough_apiv1/index.html#ngsi10-standard-operations
        # at "Update context elements"
        logging.info("Sending command")

        if params is None:
            params = {}

        url = "http://{}:{}/v1/updateContext".format(self.idas_host, self.idas_admin_port)

        additional_headers = {'Content-Type': 'application/json',
                              'Accept': 'application/json'}

        params = '|'.join(['%s' % (str(value)) for (key, value) in params.items()])
        # if params != '':
        #     params = '|' + params
        #
        # value = '{}@{}{}'.format(device_id, command, params)
        # logging.info("Command value:", value)

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

        self._send_request(url, payload, 'POST', additional_headers=additional_headers)

    def get_pooling_commands(self, sensor_id):
        logging.info("Getting pooling commands")

        url = "http://{}:{}/iot/d?k={}&i={}".format(self.idas_host, self.idas_ul20_port, self.api_key, sensor_id)
        payload = ''
        additional_headers = {'Content-Type': 'application/json'}

        self._send_request(url, payload, 'GET', additional_headers=additional_headers)
