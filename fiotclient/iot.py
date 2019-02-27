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

    def __init__(self, fiware_service='', fiware_service_path='', cb_host='', cb_port='',
                 idas_aaa='', token='', expires_at='', host_id='',
                 idas_host='', idas_admin_port='', idas_ul20_port='', api_key='',
                 mosquitto_host='', mosquitto_port=''):
        """Client for doing IoT management operations on FIWARE platform

        :param config_file: The file in which load the default configuration
        """

        super(FiwareIotClient, self).__init__(fiware_service=fiware_service, fiware_service_path=fiware_service_path,
                                              cb_host=cb_host, cb_port=cb_port,
                                              idas_aaa=idas_aaa, token=token, expires_at=expires_at,
                                              host_id=host_id)

        self.idas_host = idas_host
        self.idas_admin_port = idas_admin_port
        self.idas_ul20_port = idas_ul20_port
        self.api_key = api_key

        self.mosquitto_host = mosquitto_host
        self.mosquitto_port = mosquitto_port

    @classmethod
    def from_config_dict(cls, config_dict):
        """Client for doing IoT management operations on FIWARE platform

        :param config_dict: The python dict from which to load the default configuration
        """

        # TODO Check and notify mandatory parameters on input config dict

        return cls(fiware_service=config_dict['service']['name'],
                   fiware_service_path=config_dict['service']['path'],
                   cb_host=config_dict['context_broker']['host'], cb_port=config_dict['context_broker']['port'],
                   idas_host=config_dict['iot_agent']['host'], idas_admin_port=config_dict['iot_agent']['admin_port'],
                   idas_ul20_port=config_dict['iot_agent']['ul20_port'], api_key=config_dict['iot_agent']['api_key'],
                   mosquitto_host=config_dict['mqtt_broker']['host'], mosquitto_port=config_dict['mqtt_broker']['port'])

    @classmethod
    def from_config_file(cls, config_file):
        """Client for doing IoT management operations on FIWARE platform

        :param config_file: The file in which load the default configuration
        """

        # TODO Check and notify mandatory parameters on input config file
        config_dict = utils.read_config_file(config_file)

        return cls(fiware_service=config_dict['fiware_service'],
                   fiware_service_path=config_dict['fiware_service_path'],
                   cb_host=config_dict['cb_host'], cb_port=config_dict['cb_port'],
                   idas_aaa=config_dict['idas_aaa'], token=config_dict['token'], expires_at='',
                   host_id=config_dict['host_id'],
                   idas_host=config_dict['idas_host'], idas_admin_port=config_dict['idas_admin_port'],
                   idas_ul20_port=config_dict['idas_ul20_port'], api_key=config_dict['api_key'],
                   mosquitto_host=config_dict['mosquitto_host'], mosquitto_port=config_dict['mosquitto_port'])

    @staticmethod
    def generate_api_key():
        """Generate a random api key to be used on service creation

        :return: The generated api key string
        """
        import uuid
        return uuid.uuid1().hex

    def create_service(self, service, service_path, api_key=None):
        """Creates a new service with the given information

        :param service: The name of the service to be created
        :param service_path: The service path of the service to be created
        :param api_key: A specific api key to use to create the service.
                        If no api key is provided, a random one will be generated.
        :return: The information of the created service
        """
        logging.info("Creating service")

        if api_key:
            response = self._create_service(service, service_path, api_key)

        else:
            api_key = self.generate_api_key()

            created = False
            response = None

            while not created:
                response = self._create_service(service, service_path, api_key)

                if response['status_code'] == 201:
                    created = True
                else:
                    api_key = self.generate_api_key()

        response['api_key'] = api_key
        return response

    def _create_service(self, service, service_path, api_key):
        """Auxiliary method to try to create a service with the given information

        :param service: The name of the service to be created
        :param service_path: The service path of the service to be created
        :param api_key: The api key to use to create the service
        :return: The response of the creation request
        """
        url = "http://{}:{}/iot/services".format(self.idas_host, self.idas_admin_port)

        additional_headers = {'Content-Type': 'application/json',
                              'Fiware-Service': service,
                              'Fiware-ServicePath': service_path}

        payload = {
                    "services": [
                        {
                          "protocol": ["IoTA-UL"],  # TODO Remove hardcoded protocol
                          "apikey": str(api_key),
                          "token": "token2",
                          "cbroker": "http://{}:{}".format(self.cb_host, self.cb_port),
                          "entity_type": "thing",
                          "resource": "/iot/d"
                        }
                    ]
                  }

        return self._send_request(url, 'POST', payload=payload, additional_headers=additional_headers)

    def remove_service(self, service, service_path, api_key="", remove_devices=False):
        """Remove a subservice into a service.
        If Fiware-ServicePath is '/\*' or '/#' remove service and all its sub-services.

        :param service: The name of the service to be removed
        :param service_path: The service path of the service to be removed
        :param api_key: The api key of the service.
                        If no value is provided, default value "" will be used
        :param remove_devices: If either its to remove devices in service/subservice or not.
                               If no value is provided, the default value (False) will be used.
                               This parameter is not valid when Fiware-ServicePath is '/\*' or '/#'.
        :return: The response of the removal request
        """
        logging.info("Removing service")

        params = {
            'resource': '/iot/d',
            'apikey': api_key
        }

        url = "http://{}:{}/iot/services".format(self.idas_host, self.idas_admin_port)

        if service_path != '/*' and service_path != '/#':
            remove_devices_str = 'true' if remove_devices else 'false'
            url += '&device={}'.format(remove_devices_str)

        additional_headers = {'Fiware-Service': service,
                              'Fiware-ServicePath': service_path}

        return self._send_request(url, 'DELETE', params=params, additional_headers=additional_headers)

    def list_services(self):
        """Get all registered services

        :return: A list with the registered services
        """
        # TODO Implement
        pass

    def set_api_key(self, api_key):
        """Sets the api key to use to send measurements from device

        :param api_key: The api key of the service to use
        :return: None
        """
        self.api_key = api_key

    def register_device(self, device_schema, device_id, entity_id, endpoint='', protocol='IoTA-UL'):
        """Register a new device with the given structure in the currently selected service

        :param device_schema: JSON string representing device schema
        :param device_id: The id to the device to be created
        :param entity_id: The id to the NGSI entity created representing the device
        :param endpoint: The endpoint of the device to which actions will be sent on format IP:PORT
        :param protocol: The protocol to be used on device.
                         If no value is provided the default protocol (IoTA-UL) will be used
        :return: Information of the registered device
        """
        logging.info("Registering device")

        params = {'protocol': protocol}
        url = "http://{}:{}/iot/devices".format(self.idas_host, self.idas_admin_port)
        additional_headers = {'Content-Type': 'application/json'}

        device_schema = device_schema.replace('[DEVICE_ID]', str(device_id)) \
            .replace('[ENTITY_ID]', str(entity_id))

        if '"endpoint"' in device_schema:
            endpoint_split = endpoint.split(':')
            device_ip = endpoint_split[0]
            device_port = endpoint_split[1]
            device_schema = device_schema.replace('[DEVICE_IP]', str(device_ip)) \
                                         .replace('[PORT]', str(device_port))

        payload = json.loads(device_schema)

        return self._send_request(url, 'POST', params=params, payload=payload, additional_headers=additional_headers)

    def register_device_from_file(self, device_file_path, device_id, entity_id, endpoint='', protocol='IoTA-UL'):
        """Register a new device loading its structure from a given file

        :param device_file_path: The path to the description file for the device
        :param device_id: The id to the device to be created
        :param entity_id: The id to the NGSI entity created representing the device
        :param endpoint: The endpoint of the device to which actions will be sent on format IP:PORT
        :param protocol: The protocol to be used on device.
                         If no value is provided the default protocol (IoTA-UL) will be used
        :return: Information of the registered device
        """
        logging.info("Opening file '{}'".format(device_file_path))
        with open(device_file_path) as json_device_file:
            payload = json.load(json_device_file)

        device_schema_json_str = json.dumps(payload)
        return self.register_device(device_schema_json_str, device_id, entity_id, endpoint=endpoint, protocol=protocol)

    def update_device(self, device_schema, device_id, entity_id, endpoint='', protocol='IoTA-UL'):
        """Updates a registered device with the given structure in the currently selected service

        :param device_schema: JSON string representing device schema
        :param device_id: The id to the device to be updated
        :param entity_id: The id to the NGSI entity that represents the device
        :param endpoint: The endpoint of the device to which actions will be sent on format IP:PORT
        :param protocol: The protocol to be used on device.
                         If no value is provided the default protocol (IoTA-UL) will be used
        :return: Information of the updated device
        """
        pass
        # TODO Implement

    def remove_device(self, device_id):
        """Removes a device with the given id in the currently selected service

        :param device_id: The id to the device to be removed
        :return: Response of the removal request
        """

        url = "http://{}:{}/iot/devices/{}".format(self.idas_host, self.idas_admin_port, device_id)
        additional_headers = {'Content-Type': 'application/json'}

        return self._send_request(url, 'DELETE', additional_headers=additional_headers)

    def get_device_by_id(self, device_id):
        """Get device information given its device id

        :param device_id: The id of the device to be searched
        :return: The information of the device found with the given id
                 or None if no device was found with the id
        """
        url = "http://{}:{}/iot/devices/{}".format(self.idas_host, self.idas_admin_port, device_id)
        additional_headers = {'Content-Type': 'application/json'}

        return self._send_request(url, 'GET', additional_headers=additional_headers)

    def list_devices(self, limit=None, offset=None):
        """List the devices registered in the currently selected service

        :return: The list of devices registered in the service
        """
        logging.info("Listing devices")

        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        url = "http://{}:{}/iot/devices".format(self.idas_host, self.idas_admin_port)
        additional_headers = {'Content-Type': 'application/json'}

        return self._send_request(url, 'GET', params=params, additional_headers=additional_headers)

    @staticmethod
    def _join_group_measurements(group_measurements):
        """Auxiliary method to create a standardized string from measurements group dict

        :param group_measurements: A dict representing a group of measurements, where the keys are the attribute
                                   names and the values are the measurements values for each attribute
        :return: A string representing the measurement group
        """
        return '|'.join(['%s|%s' % (str(key), str(value)) for (key, value) in group_measurements.items()])

    @staticmethod
    def _create_ul_payload_from_measurements(measurements):
        """Auxiliary method to create a UL formatted payload string from measurement group or a list
        of measurement groups to the FIWARE platform from a device

        :param measurements: A measurement group (a dict where keys are device attributes and values are measurements
                             for each attribute) or a list of measurement groups obtained in the device
        :return: A string containing the UL payload
        """
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

        return payload

    def send_observation(self, device_id, measurements, protocol='MQTT'):
        """Sends a measurement group or a list of measurement groups from a device to the FIWARE platform

        :param device_id: The id of the device in which the measurement was obtained
        :param measurements: A measurement group (a dict where keys are device attributes and values are measurements
                             for each attribute) or a list of measurement groups obtained in the device
        :param protocol: The transport protocol to be used to send measurements.
                         Currently accepted values are 'MQTT' and 'HTTP'.
                         If no value is provided the default value (MQTT) will be used
        :return: The summary of the sent measurements
        """
        logging.info("Sending observation")

        payload = self._create_ul_payload_from_measurements(measurements)

        if protocol == 'MQTT':
            logging.info("Transport protocol: MQTT")
            topic = "/{}/{}/attrs".format(self.api_key, device_id)

            logging.info("Publishing to {} on topic {}".format(self.idas_host, topic))
            logging.info("Sending payload: ")
            logging.info(payload)

            publish.single(topic, payload=payload, hostname=self.mosquitto_host, port=self.mosquitto_port)
            logging.info("Message sent")
            return {'result': 'OK'}

        elif protocol == 'HTTP':
            logging.info("Transport protocol: UL-HTTP")

            params = {
                'k': self.api_key,
                'i': device_id
            }

            url = "http://{}:{}/iot/d".format(self.idas_host, self.idas_ul20_port)
            additional_headers = {'Content-Type': 'text/plain'}

            self._send_request(url, 'POST', params=params, payload=payload, additional_headers=additional_headers)
            return {'result': 'OK'}

        else:
            logging.error("Unknown transport protocol '{}'".format(protocol))
            error_msg = "Unknown transport protocol. Accepted values are 'MQTT' and 'HTTP'"
            return {'error': error_msg}

    def send_command(self, entity_id, device_id, command, params=None):
        """Sends a command from the FIWARE platform to a specific device
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

        payload = {
                    "contextElements": [
                      {
                        "type": "thing",
                        "isPattern": "false",
                        "id": entity_id,
                        "attributes": [
                          {
                            "name": command,
                            "type": "command",
                            "value": value
                          }
                        ]
                      }
                    ],
                    "updateAction": "UPDATE"
                  }

        return self._send_request(url, 'POST', payload=payload, additional_headers=additional_headers)

    def get_polling_commands(self, device_id, measurements):
        """Get a list of polling commands of the device with the given id when sending a measurement group
        or a list of measurement groups to the FIWARE platform from a device with POST request

        :param device_id: The id of the device to verify pooling commands
        :param measurements: A measurement group (a dict where keys are device attributes and values are measurements
                             for each attribute) or a list of measurement groups obtained in the device
        :return: The list of pooling commands of the device
        """
        logging.info("Sending measurement and getting pooling commands")

        params = {
            'k': self.api_key,
            'i': device_id,
            'getCmd': 1
        }

        url = "http://{}:{}/iot/d".format(self.idas_host, self.idas_ul20_port)
        payload = self._create_ul_payload_from_measurements(measurements)
        additional_headers = {'Content-Type': 'text/plain'}

        return self._send_request(url, 'POST', params=params, payload=payload, additional_headers=additional_headers)
