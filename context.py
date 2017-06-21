import configparser
import json

import requests

from common import SimpleClient


class FiwareContextClient(SimpleClient):

    def __init__(self, config_file):
        super(SimpleClient, self).__init__()

        # Load the default configuration file
        with open(config_file, 'r+') as f:
            sample_config = f.read()
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_string(sample_config)

        self.cb_host = config.get('contextbroker', 'host')
        self.cb_port = config.get('contextbroker', 'port')

        self.sth_host = config.get('sthcomet', 'host')
        self.sth_port = config.get('sthcomet', 'port')

        self.cygnus_host = config.get('cygnus', 'host')
        self.cygnus_notification_host = config.get('cygnus', 'notification_host')
        self.cygnus_port = config.get('cygnus', 'port')

        self.perseo_host = config.get('perseo', 'host')
        self.perseo_port = config.get('perseo', 'port')

        f.close()

    def get_entity_by_id(self, id):
        print("===== GETTING ENTITY BY ID '{}'=====".format(id))

        url = "http://{}:{}/v2/entities/{}/attrs?type=thing".format(self.cb_host, self.cb_port, id)
        payload = ''

        self._send_request(url, payload, 'GET', format_json_response=True)

    def get_entities_by_type(self, type):
        print("===== GETTING ENTITIES BY TYPE '{}'=====".format(type))

        url = "http://{}:{}/v2/entities?type={}".format(self.cb_host, self.cb_port, type)

        headers = {'X-Auth-Token': self.token,  # TODO Use token from common client
                   'Fiware-Service': self.fiware_service,
                   'Fiware-ServicePath': self.fiware_service_path}

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

        answer = str(input("Do you want me to print all entities data? (yes/no)"))
        if answer == "yes" or answer == "y":
            print(json.dumps(entities, indent=4))

        print()

    def list_subscriptions(self):
        print("===== LISTING SUBSCRIPTIONS =====")

        url = "http://{}:{}/v2/subscriptions".format(self.cb_host, self.cb_port)

        payload = ''

        self._send_request(url, payload, 'GET', format_json_response=True)

    def unsubscribe(self, subscription_id):
        print("===== REMOVING SUBSCRIPTION =====")

        url = "http://{}:{}/v1/unsubscribeContext".format(self.cb_host, self.cb_port)
        
        additional_headers = {'Accept': 'application/json',
                              'Content-Type': 'application/json'}

        payload = {"subscriptionId": str(subscription_id)}

        self._send_request(url, payload, 'POST', additional_headers=additional_headers)

    def subscribe_attributes_change(self, device_id, attributes, notification_url):
        print("===== SUBSCRIBING TO ATTRIBUTES '{}' CHANGE =====".format(attributes))

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

        self._send_request(url, payload, 'POST', additional_headers=additional_headers)

    def subscribe_cygnus(self, entity_id, attributes):
        print("===== SUBSCRIBING CYGNUS =====")

        notification_url = "http://{}:{}/notify".format(self.cygnus_notification_host, self.cygnus_port)
        self.subscribe_attributes_change(entity_id, attributes, notification_url)

    def subscribe_historical_data(self, entity_id, attributes):
        print("===== SUBSCRIBING TO HISTORICAL DATA =====")

        notification_url = "http://{}:{}/notify".format(self.sth_host, self.sth_port)
        self.subscribe_attributes_change(entity_id, attributes, notification_url)

    def create_attribute_change_rule(self, attribute, attribute_type, condition, notification_url, action='post'):
        print("===== CREATE ATTRIBUTE CHANGE RULE =====")

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
            print("Unknown action '{}'".format(action))
            return

        self._send_request(url, payload, 'POST', format_json_response=True, additional_headers=additional_headers)

    def get_historical_data(self, entity_type, entity_id, attribute, items_number=10):
        print("===== GETTING HISTORICAL DATA =====")

        url = "http://{}:{}/STH/v1/contextEntities/type/{}/id/{}/attributes/{}?lastN={}".format(self.sth_host,
                                                                                                self.sth_port,
                                                                                                entity_type,
                                                                                                entity_id,
                                                                                                attribute,
                                                                                                items_number)

        additional_headers = {'Accept': 'application/json',
                              'Fiware-Service': str(self.fiware_service).lower(),
                              'Fiware-ServicePath': str(self.fiware_service_path).lower()}

        payload = ''

        self._send_request(url, payload, 'GET', format_json_response=True, additional_headers=additional_headers)
