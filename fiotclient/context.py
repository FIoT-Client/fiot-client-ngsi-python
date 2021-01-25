import json
import logging

from . import BaseClient
from .config import FiwareConfig


class FiwareContextClient(BaseClient):

    def __init__(self, fiware_config: FiwareConfig):
        """Client for doing context management operations on FIWARE platform

        :param fiware_config: The FiwareConfig object from which to load the default configuration
        """
        super(FiwareContextClient, self).__init__(fiware_config)

        self.cb_url = f"http://{self.fiware_config.cb_host}:{self.fiware_config.cb_port}"
        self.perseo_url = f"http://{self.fiware_config.perseo_host}:{self.fiware_config.perseo_port}"
        self.cygnus_notification_url = f"http://{self.fiware_config.cygnus_notification_host}:{self.fiware_config.cygnus_port}"
        self.sth_url = f"http://{self.fiware_config.sth_host}:{self.fiware_config.sth_port}"

    def create_entity(self, entity_schema, entity_type, entity_id):
        """Creates a new NGSI entity with the given structure in the currently selected service

        :param entity_schema: JSON string representing entity schema
        :param entity_type: The type of the entity to be created
        :param entity_id: The id to the entity to be created

        :return: Information of the registered entity
        """
        url = f"{self.cb_url}/v2/entities"
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
        logging.debug(f"Reading file '{entity_file_path}'")
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
        url = f"{self.cb_url}/v2/entities/{entity_id}"

        return self._send_request(url, 'DELETE', params=params)

    def get_entity_by_id(self, entity_id, entity_type):
        """Get entity information given its entity id

        :param entity_id: The id of the entity to be searched
        :param entity_type: The type of the entity to be searched
        :return: The information of the entity found with the given id
                 or None if no entity was found with the id
        """
        params = {'type': entity_type}
        url = f"{self.cb_url}/v2/entities/{entity_id}"

        return self._send_request(url, 'GET', params=params)

    def get_entities_by_type(self, entity_type):
        """Get entities created with a given entity type

        :param entity_type: The type of the entities to be searched
        :return: A list with the information of the entities found with the given type
        """
        params = {'type': entity_type}

        url = f"{self.cb_url}/v2/entities"

        return self._send_request(url, 'GET', params=params)

    def get_entities(self, entity_type=None, id_pattern=None, q=None, limit=None, offset=None, options=None):
        """Get all created entities

        :return: A list with the information of all the created entities
        """
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

        url = f"{self.cb_url}/v2/entities"

        return self._send_request(url, 'GET', params=params)

    def subscribe_attributes_change(self, entity_id, entity_type, attributes, notification_url):
        """Create a new subscription on given attributes of the entity with the specified id and type

        :param entity_id: The id of the entity to be monitored
        :param entity_type: The type of the entity to be monitored
        :param attributes: The list of attributes do be monitored
        :param notification_url: The URL to which the notification will be sent on changes
        :return: The information of the subscription
        """
        url = f"{self.cb_url}/v1/subscribeContext"

        additional_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        payload = {
            "entities": [{
                "type": str(entity_type),
                "isPattern": "false",
                "id": str(entity_id)
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
        url = f"{self.perseo_url}/rules"

        additional_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        payload = {
            "name": f"{attribute}-rule",
            "text": f"select *,\"{attribute}-rule\" as ruleName from pattern [every ev=iotEvent(cast(cast(ev.{attribute}?,String),{attribute_type}){condition})]",
            "action": {
                "type": "",
                "template": f"Alert! {attribute} is now ${{ev.{attribute}}}.",
                "parameters": {}
            }
        }

        if action == 'email':
            payload["action"]["type"] = "email"
            # TODO Remove hardcoded info
            payload["action"]["parameters"] = {"to": f"{'lucascristiano27@gmail.com'}",
                                               "from": f"{'lucas.calixto.dantas@gmail.com'}",
                                               "subject": f"Alert! High {attribute.capitalize()} detected"}
        elif action == 'post':
            payload["action"]["type"] = "post"
            payload["action"]["parameters"] = {"url": f"{notification_url}"}

        else:
            error_msg = f"Unknown action '{action}'"
            logging.error(error_msg)
            return {'error': error_msg}

        return self._send_request(url, 'POST', payload=payload, additional_headers=additional_headers)

    def subscribe_cygnus(self, entity_id, attributes):
        """Create a new subscription on attributes to send changes on its values to sinks configured on Cygnus

        :param entity_id: The id of the entity to be monitored
        :param attributes: The list of attributes do be monitored
        :return: The information of the subscription
        """
        notification_url = f"{self.cygnus_notification_url}/notify"
        return self.subscribe_attributes_change(entity_id, attributes, notification_url)

    def subscribe_historical_data(self, entity_id, attributes):
        """Create a new subscription on attributes to store changes on its values as historical data

        :param entity_id: The id of the entity to be monitored
        :param attributes: The list of attributes do be monitored
        :return: The information of the subscription
        """
        notification_url = f"{self.sth_url}/notify"
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
        params = {'lastN': items_number}

        url = f"http://{self.sth_url}/STH/v1/contextEntities/type/{entity_type}/id/{entity_id}/attributes/{attribute}"

        additional_headers = {
            'Accept': 'application/json',
            'Fiware-Service': str(self.fiware_config.service).lower(),
            'Fiware-ServicePath': str(self.fiware_config.service_path).lower()
        }

        return self._send_request(url, 'GET', params=params, additional_headers=additional_headers)

    def unsubscribe(self, subscription_id):
        """Remove a subscription with the given subscription id

        :param subscription_id: The id of the subscription to be removed
        :return: True if the subscription with the given id was removed
                 False if no subscription with the given id was removed
        """
        url = f"{self.cb_url}/v1/unsubscribeContext"

        additional_headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

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
        url = f"{self.cb_url}/v2/subscriptions/{subscription_id}"

        return self._send_request(url, 'GET')

    def list_subscriptions(self):
        """Get all subscriptions

        :return: A list with the ids of all the subscriptions
        """
        url = f"{self.cb_url}/v2/subscriptions"

        return self._send_request(url, 'GET')
