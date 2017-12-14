import json
import logging

import requests

from fiotclient import utils

__author__ = "Lucas Cristiano Calixto Dantas"
__copyright__ = "Copyright 2017, Lucas Cristiano Calixto Dantas"
__credits__ = ["Lucas Cristiano Calixto Dantas"]
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Lucas Cristiano Calixto Dantas"
__email__ = "lucascristiano27@gmail.com"
__status__ = "Development"


class SimpleClient(object):

    def __init__(self, config_file):
        """Default client for making requests to FIWARE APIs

        :param config_file: The file in which load the default configuration
        """
        logging.basicConfig(filename='fiotclient.log', level=logging.DEBUG)

        config_dict = utils.read_config_file(config_file)

        self.fiware_service = config_dict['fiware_service']
        self.fiware_service_path = config_dict['fiware_service_path']

        self.cb_host = config_dict['cb_host']
        self.cb_port = config_dict['cb_port']

        self.idas_aaa = config_dict['idas_aaa']
        self.token = config_dict['token']
        self.expires_at = ''

        self.host_id = config_dict['host_id']

    def _send_request(self, url, payload, method, additional_headers=None):
        """Auxiliary method to configure and execute a request to FIWARE APIs

        :param url: The url to be called on the request
        :param payload: The payload to be sent on the request
        :param method: The method to be used on the request
        :param additional_headers: Additional http headers to be used in the request
        :return: The response from the request execution
        """
        default_headers = {'X-Auth-Token': self.token,
                           'Fiware-Service': self.fiware_service,
                           'Fiware-ServicePath': self.fiware_service_path}

        if additional_headers is None:
            additional_headers = {}

        headers = utils.merge_dicts(default_headers, additional_headers)

        logging.debug("Asking to {}".format(url))
        logging.debug("Headers:")
        logging.debug(json.dumps(headers, indent=4))

        if not isinstance(payload, str):
            str_payload = json.dumps(payload, indent=4)
        else:
            str_payload = payload

        if str_payload != '':
            logging.debug("Sending payload:")
            logging.debug(str_payload)

        # TODO Adds timeout or verifications of servers on calls to APIs

        if method == 'GET':
            r = requests.get(url, data=str_payload, headers=headers)
        elif method == 'POST':
            r = requests.post(url, data=str_payload, headers=headers)
        elif method == 'PUT':
            r = requests.put(url, data=str_payload, headers=headers)
        elif method == 'DELETE':
            r = requests.delete(url, data=str_payload, headers=headers)
        else:
            logging.error("Unsupported method '{}'".format(str(method)))
            error_msg = "Unsupported method. Select one of 'GET', 'POST', 'PUT' and 'DELETE'".format(method)
            return {'error': error_msg}

        status_code = r.status_code
        logging.debug("Status Code: {}".format(str(status_code)))

        response = json.loads(r.text) if r.text != '' else {}

        logging.debug("Response: ")
        logging.debug(json.dumps(response, indent=4))

        return {'status_code': status_code,
                'response': response}

    def authenticate(self, username, password):
        """Generates an authentication token based on user credentials using FIWARE Lab OAuth2.0 Authentication system
           If you didn't have a user, go and register first at http://cloud.fiware.org

        :param username: the user's username from Fiware authentication account
        :param password: the user's password from Fiware authentication account
        :return: the generated token and expiration
        """

        logging.info('Generating token')

        tokens_url = "http://cloud.lab.fi-ware.org:4730/v2.0/tokens"

        payload = {
            "auth": {
                "passwordCredentials": {
                    "username": str(username),
                    "password": str(password)
                }
            }
        }

        headers = {'Content-Type': 'application/json'}
        url = tokens_url

        resp = requests.post(url, data=json.dumps(payload), headers=headers)

        self.token = resp.json()["access"]["token"]["id"]
        self.expires_at = resp.json()["access"]["token"]["expires"]

        logging.debug("FIWARE OAuth2.0 Token: {}".format(self.token))
        logging.debug("Token expiration: {}".format(self.expires_at))

    def set_service(self, service, service_path):
        """Specify the service context to use on operations

        :param service: The name of the service to be used
        :param service_path: The service path of the service to be used
        :return: None
        """
        self.fiware_service = service
        self.fiware_service_path = service_path
