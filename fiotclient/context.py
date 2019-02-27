import json
import logging

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


class FiwareContextClient(SimpleClient):

    def __init__(self, fiware_service='', fiware_service_path='', cb_host='', cb_port='',
                 idas_aaa='', token='', expires_at='', host_id='',
                 sth_host='', sth_port='',
                 cygnus_host='', cygnus_notification_host='', cygnus_port='',
                 perseo_host='', perseo_port=''):
        """Client for doing context management operations on FIWARE platform"""

        super(FiwareContextClient, self).__init__(fiware_service=fiware_service,
                                                  fiware_service_path=fiware_service_path,
                                                  cb_host=cb_host, cb_port=cb_port,
                                                  idas_aaa=idas_aaa, token=token, expires_at=expires_at,
                                                  host_id=host_id)

        self.sth_host = sth_host
        self.sth_port = sth_port

        self.cygnus_host = cygnus_host
        self.cygnus_notification_host = cygnus_notification_host
        self.cygnus_port = cygnus_port

        self.perseo_host = perseo_host
        self.perseo_port = perseo_port

    @classmethod
    def from_config_dict(cls, config_dict):
        """Client for doing context management operations on FIWARE platform

        :param config_dict: The python dict from which to load the default configuration
        """

        # TODO Check and notify mandatory parameters on input config dict

        return cls(fiware_service=config_dict['service']['name'],
                   fiware_service_path=config_dict['service']['path'],
                   cb_host=config_dict['context_broker']['host'], cb_port=config_dict['context_broker']['port'],
                   sth_host=config_dict['sth']['host'], sth_port=config_dict['sth']['port'],
                   cygnus_host=config_dict['cygnus']['host'],
                   cygnus_port=config_dict['cygnus']['port'],
                   cygnus_notification_host=config_dict['cygnus']['notification_host'],
                   perseo_host=config_dict['perseo']['host'],
                   perseo_port=config_dict['perseo']['port'])

    @classmethod
    def from_config_file(cls, config_file):
        """Client for doing context management operations on FIWARE platform

        :param config_file: The file in which load the default configuration
        """

        # TODO Check and notify mandatory parameters on input config file
        config_dict = utils.read_config_file(config_file)

        return cls(fiware_service=config_dict['fiware_service'],
                   fiware_service_path=config_dict['fiware_service_path'],
                   cb_host=config_dict['cb_host'], cb_port=config_dict['cb_port'],
                   idas_aaa=config_dict['idas_aaa'], token=config_dict['token'], expires_at='',
                   host_id=config_dict['host_id'],
                   sth_host=config_dict['sth_host'], sth_port=config_dict['sth_port'],
                   cygnus_host=config_dict['cygnus_host'],
                   cygnus_notification_host=config_dict['cygnus_notification_host'],
                   cygnus_port=config_dict['cygnus_port'],
                   perseo_host=config_dict['perseo_host'],
                   perseo_port=config_dict['perseo_port'])

    def create_entity(self, entity_schema, entity_type, entity_id):
        """Creates a new NGSI entity with the given structure in the currently selected service

        :param entity_schema: JSON string representing entity schema
        :param entity_type: The type of the entity to be created
        :param entity_id: The id to the entity to be created

        :return: Information of the registered entity
        """
        url = "http://{}:{}/v2/entities".format(self.cb_host, self.cb_port)
        additional_headers = {'Content-Type': 'application/json'}

        entity_schema = entity_schema.replace('[ENTITY_TYPE]', str(entity_type))
        entity_schema = entity_schema.replace('[ENTITY_ID]', str(entity_id))

        payload = json.loads(entity_schema)

        return self._send_request(url, 'POST', payload=payload, additional_headers=additional_headers)

    def create_entity_from_file(self, entity_file_path, entity_type, entity_id):
        """Creates a new NGSI entity loading its structure from a given file

        :param entity_file_path: The path to the description file for the entity
        :param entity_type: The type of the entity to be created
        :param entity_id: The id to the entity to be created

        :return: Information of the registered entity
        """
        logging.info("Opening file '{}'".format(entity_file_path))
        with open(entity_file_path) as json_entity_file:
            payload = json.load(json_entity_file)

        entity_schema_json_str = json.dumps(payload)

        return self.create_entity(entity_schema_json_str, entity_type, entity_id)

    def update_entity(self, entity_id, entity_schema):
        """Updates an entity with the given id for the new structure in the currently selected service

        :param entity_id: The id to the entity to be updated
        :param entity_schema: JSON string representing new entity schema

        :return: Information of the updated entity
        """
        # TODO Implement
        pass

    def remove_entity(self, entity_type, entity_id):
        """Removes an entity with the given id

        :param entity_type: The type of the entity to be removed
        :param entity_id: The id to the entity to be removed

        :return: Information of the removed entity
        """

        params = {'type': entity_type}
        url = "http://{}:{}/v2/entities/{}".format(self.cb_host, self.cb_port, entity_id)

        return self._send_request(url, 'DELETE', params=params)

    def get_entity_by_id(self, entity_id, entity_type):
        """Get entity information given its entity id

        :param entity_id: The id of the entity to be searched
        :param entity_type: The type of the entity to be searched
        :return: The information of the entity found with the given id
                 or None if no entity was found with the id
        """
        logging.info("Getting entity by id '{}'".format(entity_id))

        params = {'type': entity_type}
        url = "http://{}:{}/v2/entities/{}".format(self.cb_host, self.cb_port, entity_id)

        return self._send_request(url, 'GET', params=params)

    def get_entities_by_type(self, entity_type):
        """Get entities created with a given entity type

        :param entity_type: The type of the entities to be searched
        :return: A list with the information of the entities found with the given type
        """
        logging.info("Getting entities by type '{}'".format(type))

        params = {'type': entity_type}

        url = "http://{}:{}/v2/entities".format(self.cb_host, self.cb_port)

        return self._send_request(url, 'GET', params=params)

    def get_entities(self, entity_type=None, id_pattern=None, q=None, limit=None, offset=None, options=None):
        """Get all created entities

        :return: A list with the information of all the created entities
        """
        logging.info("Getting all entities")

        params = {}

        if entity_type:
            params['type'] = entity_type
        if id_pattern:
            params['idPattern'] = id_pattern
        if q:
            params['q'] = q
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if options:
            params['options'] = options

        url = "http://{}:{}/v2/entities".format(self.cb_host, self.cb_port)

        return self._send_request(url, 'GET', params=params)

    def subscribe_attributes_change(self, device_id, attributes, notification_url):
        """Create a new subscription on given attributes of the device with the specified id

        :param device_id: The id of the device to be monitored
        :param attributes: The list of attributes do be monitored
        :param notification_url: The URL to which the notification will be sent on changes
        :return: The information of the subscription
        """
        logging.info("Subscribing for change on attributes '{}' on device with id '{}'".format(attributes, device_id))

        url = "http://{}:{}/v1/subscribeContext".format(self.cb_host, self.cb_port)

        additional_headers = {'Accept': 'application/json',
                              'Content-Type': 'application/json'}

        payload = {"entities": [{
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

        return self._send_request(url, 'POST', payload=payload, additional_headers=additional_headers)

    def subscribe_attribute_change_with_rule(self, attribute, attribute_type, condition, action='post', notification_url=None):
        """Register a new rule to be evaluated on attribute values change and a action to be taken when rule evaluated to true

        :param attribute: The attribute to be monitored
        :param attribute_type: The type of the attribute to be monitored
        :param condition: The condition to be evaluated on changes on attribute's value
        :param action: The action type to be taken when condition is evaluated true.
                       Currently accepted values to this parameter are 'email' and 'post'
        :param notification_url: The endpoint to which POST notifications will be sent
        :return: The information of the created rule
        """
        logging.info("Creating attribute change rule")

        url = "http://{}:{}/rules".format(self.perseo_host, self.perseo_port)

        additional_headers = {'Accept': 'application/json',
                              'Content-Type': 'application/json'}

        rule_template = "select *,\"{}-rule\" as ruleName from pattern " \
                        "[every ev=iotEvent(cast(cast(ev.{}?,String),{}){})]"
        payload = {
            "name": "{}-rule".format(attribute),
            "text": rule_template.format(attribute, attribute, attribute_type, condition),
            "action": {
                "type": "",
                "template": "Alert! {0} is now ${{ev.{1}}}.".format(attribute, attribute),
                "parameters": {}
            }
        }

        if action == 'email':
            payload["action"]["type"] = "email"
            # TODO Remove hardcoded info
            payload["action"]["parameters"] = {"to": "{}".format("lucascristiano27@gmail.com"),
                                               "from": "{}".format("lucas.calixto.dantas@gmail.com"),
                                               "subject": "Alert! High {} Detected".format(attribute.capitalize())}
        elif action == 'post':
            payload["action"]["type"] = "post"
            payload["action"]["parameters"] = {"url": "{}".format(notification_url)}

        else:
            error_msg = "Unknown action '{}'".format(action)
            logging.error(error_msg)
            return {'error': error_msg}

        return self._send_request(url, 'POST', payload=payload, additional_headers=additional_headers)

    def subscribe_cygnus(self, entity_id, attributes):
        """Create a new subscription on attributes to send changes on its values to sinks configured on Cygnus

        :param entity_id: The id of the entity to be monitored
        :param attributes: The list of attributes do be monitored
        :return: The information of the subscription
        """
        logging.info("Subscribing Cygnus")

        notification_url = "http://{}:{}/notify".format(self.cygnus_notification_host, self.cygnus_port)
        return self.subscribe_attributes_change(entity_id, attributes, notification_url)

    def subscribe_historical_data(self, entity_id, attributes):
        """Create a new subscription on attributes to store changes on its values as historical data

        :param entity_id: The id of the entity to be monitored
        :param attributes: The list of attributes do be monitored
        :return: The information of the subscription
        """
        logging.info("Subscribing to historical data")

        notification_url = "http://{}:{}/notify".format(self.sth_host, self.sth_port)
        return self.subscribe_attributes_change(entity_id, attributes, notification_url)

    def get_historical_data(self, entity_type, entity_id, attribute, items_number=10):
        """Get historical data from a specific attribute of an entity

        :param entity_type: The type of the entity to get historical data
        :param entity_id: The id of the entity to get historical data
        :param attribute: The attribute of the entity to get historical data
        :param items_number: The number of last entries to be queried.
                             If no value is provided, the default value (10 entries) will be used
        :return: The historical data on the specified attribute of the given entity
        """
        logging.info("Getting historical data")

        params = {'lastN': items_number}

        url = "http://{}:{}/STH/v1/contextEntities/type/{}/id/{}/attributes/{}".format(
            self.sth_host, self.sth_port, entity_type, entity_id, attribute)

        additional_headers = {'Accept': 'application/json',
                              'Fiware-Service': str(self.fiware_service).lower(),
                              'Fiware-ServicePath': str(self.fiware_service_path).lower()}

        return self._send_request(url, 'GET', params=params, additional_headers=additional_headers)

    def unsubscribe(self, subscription_id):
        """Remove a subscription with the given subscription id

        :param subscription_id: The id of the subscription to be removed
        :return: True if the subscription with the given id was removed
                 False if no subscription with the given id was removed
        """
        logging.info("Removing subscriptions")

        url = "http://{}:{}/v1/unsubscribeContext".format(self.cb_host, self.cb_port)

        additional_headers = {'Accept': 'application/json',
                              'Content-Type': 'application/json'}

        payload = {
            "subscriptionId": str(subscription_id)
        }

        return self._send_request(url, 'POST', payload=payload, additional_headers=additional_headers)

    def get_subscription_by_id(self, subscription_id):
        """Get subscription information given its subscription id

        :param subscription_id: The id of the subscription to be searched
        :return: The information of the subscription found with the given id
                 or None if no subscription was found with the id
        """
        logging.info("Getting subscription by id '{}'".format(subscription_id))

        url = "http://{}:{}/v2/subscriptions/{}".format(self.cb_host, self.cb_port, subscription_id)

        return self._send_request(url, 'GET')

    def list_subscriptions(self):
        """Get all subscriptions

        :return: A list with the ids of all the subscriptions
        """
        logging.info("Listing subscriptions")

        url = "http://{}:{}/v2/subscriptions".format(self.cb_host, self.cb_port)

        return self._send_request(url, 'GET')
