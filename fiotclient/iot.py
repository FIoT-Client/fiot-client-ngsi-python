import json
import logging

import paho.mqtt.publish as publish

from . import BaseClient
from .config import FiwareConfig


class FiwareIotClient(BaseClient):

    def __init__(self, fiware_config: FiwareConfig):
        """Client for doing IoT management operations on FIWARE platform

        :param fiware_config: The FiwareConfig object from which to load the default configuration
        """
        super(FiwareIotClient, self).__init__(fiware_config)

        self.api_key = self.fiware_config.api_key

        self.cb_url = f"http://{self.fiware_config.cb_host}:{self.fiware_config.cb_port}"
        self.iota_north_url = f"http://{self.fiware_config.iota_host}:{self.fiware_config.iota_north_port}"
        self.iota_protocol_url = f"http://{self.fiware_config.iota_host}:{self.fiware_config.iota_protocol_port}"
        self.mqtt_broker_url = f"{self.fiware_config.mqtt_broker_host}:{self.fiware_config.mqtt_broker_port}"

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
        response = None
        if api_key:
            response = self._create_service(service, service_path, api_key)
            response['api_key'] = api_key
        else:
            retries = 0
            while retries < 5:
                generated_api_key = self.generate_api_key()
                response = self._create_service(service, service_path, generated_api_key)
                if response and response['status_code'] == 201:
                    response['api_key'] = generated_api_key
                    break
                retries += 1

        return response

    def _create_service(self, service, service_path, api_key):
        """Auxiliary method to try to create a service with the given information

        :param service: The name of the service to be created
        :param service_path: The service path of the service to be created
        :param api_key: The api key to use to create the service
        :return: The response of the creation request
        """
        url = f"{self.iota_north_url}/iot/services"

        additional_headers = {
            'Content-Type': 'application/json',
            'Fiware-Service': service,
            'Fiware-ServicePath': service_path
        }

        payload = {
            "services": [
                {
                  "apikey": str(api_key),
                  "cbroker": f"{self.cb_url}",
                  "entity_type": "Thing",
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
        params = {
            'resource': '/iot/d',
            'apikey': api_key
        }

        url = f"{self.iota_north_url}/iot/services"

        if service_path != '/*' and service_path != '/#':
            remove_devices_str = 'true' if remove_devices else 'false'
            url += f'&device={remove_devices_str}'

        additional_headers = {
            'Fiware-Service': service,
            'Fiware-ServicePath': service_path
        }

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
        params = {'protocol': protocol}
        url = f"{self.iota_north_url}/iot/devices"
        additional_headers = {'Content-Type': 'application/json'}

        device_schema = device_schema.replace('[DEVICE_ID]', str(device_id)) \
            .replace('[ENTITY_ID]', str(entity_id))

        if endpoint and '"endpoint"' in device_schema:
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
        logging.debug(f"Reading file '{device_file_path}'")
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
        url = f"{self.iota_north_url}/iot/devices/{device_id}"
        additional_headers = {'Content-Type': 'application/json'}

        return self._send_request(url, 'DELETE', additional_headers=additional_headers)

    def get_device_by_id(self, device_id):
        """Get device information given its device id

        :param device_id: The id of the device to be searched
        :return: The information of the device found with the given id
                 or None if no device was found with the id
        """
        url = f"{self.iota_north_url}/iot/devices/{device_id}"
        additional_headers = {'Content-Type': 'application/json'}

        return self._send_request(url, 'GET', additional_headers=additional_headers)

    def list_devices(self, limit=None, offset=None):
        """List the devices registered in the currently selected service

        :return: The list of devices registered in the service
        """
        params = {}
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset

        url = f"{self.iota_north_url}/iot/devices"
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

    def send_observation(self, device_id, measurements, protocol='MQTT', timeout=10):
        """Sends a measurement group or a list of measurement groups from a device to the FIWARE platform

        :param device_id: The id of the device in which the measurement was obtained
        :param measurements: A measurement group (a dict where keys are device attributes and values are measurements
                             for each attribute) or a list of measurement groups obtained in the device
        :param protocol: The transport protocol to be used to send measurements.
                         Currently accepted values are 'MQTT' and 'HTTP'.
                         If no value is provided the default value (MQTT) will be used
        :param timeout: The timeout for the observation send request
        :return: The summary of the sent measurements
        """
        payload = self._create_ul_payload_from_measurements(measurements)

        if protocol == 'MQTT':
            logging.debug("Transport protocol: MQTT")
            topic = f"/{self.api_key}/{device_id}/attrs"

            logging.info(f"Publishing to {self.mqtt_broker_url} on topic {topic}")
            logging.debug(f"Payload: {payload}")

            publish.single(topic, payload=payload,
                           hostname=self.fiware_config.mqtt_broker_host,
                           port=self.fiware_config.mqtt_broker_port,
                           keepalive=timeout)
            return {'result': 'OK'}

        elif protocol == 'HTTP':
            logging.debug("Transport protocol: UL-HTTP")

            params = {
                'k': self.api_key,
                'i': device_id
            }

            url = f"{self.iota_protocol_url}/iot/d"
            additional_headers = {'Content-Type': 'text/plain'}

            self._send_request(url, 'POST', params=params, payload=payload, additional_headers=additional_headers,
                               timeout=timeout)
            return {'result': 'OK'}

        else:
            logging.error(f"Unknown transport protocol '{protocol}'")
            error_msg = "Unknown transport protocol. Accepted values are 'MQTT' and 'HTTP'"
            return {'error': error_msg}

    def get_polling_commands(self, device_id, measurements):
        """Get a list of polling commands of the device with the given id when sending a measurement group
        or a list of measurement groups to the FIWARE platform from a device with POST request

        :param device_id: The id of the device to verify pooling commands
        :param measurements: A measurement group (a dict where keys are device attributes and values are measurements
                             for each attribute) or a list of measurement groups obtained in the device
        :return: The list of pooling commands of the device
        """
        params = {
            'k': self.api_key,
            'i': device_id,
            'getCmd': 1
        }

        url = f"{self.iota_protocol_url}/iot/d"
        payload = self._create_ul_payload_from_measurements(measurements)
        additional_headers = {'Content-Type': 'text/plain'}

        return self._send_request(url, 'POST', params=params, payload=payload, additional_headers=additional_headers)

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
        if params is None:
            params = {}

        url = f"{self.iota_north_url}/v1/updateContext"

        additional_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        params = '|'.join(['%s' % (str(value)) for (key, value) in params.items()])
        # if params != '':
        #     params = '|' + params
        #
        # value = f'{device_id}@{command}{params}'
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
