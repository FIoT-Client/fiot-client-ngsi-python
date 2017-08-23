import json
import logging

import paho.mqtt.publish as publish

from fiotclient import utils
from . import SimpleClient

__author__ = "Lucas Cristiano Calixto Dantas"
__copyright__ = "Copyright 2017, Lucas Cristiano Calixto Dantas"
__credits__ = ["Lucas Cristiano Calixto Dantas"]
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Lucas Cristiano Calixto Dantas"
__email__ = "lucascristiano27@gmail.com"
__status__ = "Development"


class FiwareIotClient(SimpleClient):

    def __init__(self, config_file):
        """Client for doing IoT management operations on FIWARE platform

        :param config_file: The file in which load the default configuration
        """
        super().__init__(config_file)

        config_dict = utils.read_config_file(config_file)

        self.idas_host = config_dict['idas_host']
        self.idas_admin_port = config_dict['idas_admin_port']
        self.idas_ul20_port = config_dict['idas_ul20_port']
        self.api_key = config_dict['api_key']

        self.mosquitto_host = config_dict['mosquitto_host']
        self.mosquitto_port = config_dict['mosquitto_port']

    def create_service(self, service, service_path, api_key=None):
        """Creates a new service with the given information

        :param service: The name of the service to be created
        :param service_path: The service path of the service to be created
        :param api_key: A specific api key to use to create the service.
                        If no api key is provided, a random one will be generated.
        :return: The information of the created service
        """
        logging.info("Creating service")

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
        """Auxiliary method to try to create a service with the given information

        :param url: The url to send the request
        :param api_key: The api key to use to create the service
        :param additional_headers: The additional headers set to send the request
        :return: The response of the creation request
        """
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
        """Sets the api key to use to send measurements from device

        :param api_key: The api key of the service to use
        :return: None
        """
        self.api_key = api_key

    def list_devices(self):
        """List the devices registered in the currently selected service

        :return: The list of devices registered in the service
        """
        logging.info("Listing devices")

        url = "http://{}:{}/iot/devices".format(self.idas_host, self.idas_admin_port)
        additional_headers = {'Content-Type': 'application/json'}
        payload = ''

        return self._send_request(url, payload, 'GET', additional_headers=additional_headers)

    def register_device(self, device_file_path, device_id, entity_id, device_ip='', device_port='', protocol='IoTA-UL'):
        """Register a new device with the given structure in the currently selected service

        :param device_file_path: The path to the description file for the device
        :param device_id: The id to the device to be created
        :param entity_id: The id to the NGSI entity created representing the device
        :param device_ip: The endpoint of the device to which actions will be sent
        :param device_port: The port of the device to which actions will be sent
        :param protocol: The protocol to be used on device registration.
                         If no value is provided the default protocol (IoTA-UL) will be used
        :return: Information of the registered device
        """

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
        """Auxiliary method to create a standardized string from measurements group dict

        :param group_measurements: A dict representing a group of measurements, where the keys are the attribute
                                   names and the values are the measurements values for each attribute
        :return: A string representing the measurement group
        """
        return '|'.join(['%s|%s' % (str(key), str(value)) for (key, value) in group_measurements.items()])

    def send_observation(self, device_id, measurements, protocol='MQTT'):
        """Sends a measurement group or a list of measurement groups to the FIWARE platform from a device

        :param device_id: The id of the device in which the measurement was obtained
        :param measurements: A measurement group (a dict where keys are device attributes and values are measurements
                             for each attribute) or a list of measurement groups obtained in the device
        :param protocol: The transport protocol to be used to send measurements.
                         Currently accepted values are 'MQTT' and 'HTTP'.
                         If no value is provided the default value (MQTT) will be used
        :return: The summary of the sent measurements
        """
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
        """Sends a command to a device the FIWARE platform
           (http://fiware-orion.readthedocs.io/en/latest/user/walkthrough_apiv1/index.html#ngsi10-standard-operations at
           "Update context elements" section)

        :param entity_id: The id of the entity that represents the device
        :param device_id: The id of the device to which the command will be sent
        :param command: The name of the command to be called on the device
        :param params: The command parameters to be sent
        :return: The result of the command call
        """
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

    def get_pooling_commands(self, device_id):
        """Get a list of pooling commands of the device with the given id

        :param device_id: The id of the device to verify pooling commands
        :return: The list of pooling commands of the device
        """

        logging.info("Getting pooling commands")

        url = "http://{}:{}/iot/d?k={}&i={}".format(self.idas_host, self.idas_ul20_port, self.api_key, device_id)
        payload = ''
        additional_headers = {'Content-Type': 'application/json'}

        self._send_request(url, payload, 'GET', additional_headers=additional_headers)
