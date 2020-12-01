import json
import logging

import requests

from fiotclient import utils
from fiotclient.config import FiwareConfig


def _log_request_url(method: str, url: str, params: dict, headers: dict):
    params_str = '&'.join(map(lambda key: f'{key}={params[key]}', params.keys())) if params else ''
    if params_str:
        logging.info(f"{method} {url}?{params_str} {headers}")
    else:
        logging.info(f"{method} {url} {headers}")


def _log_request(method, url, params, headers, str_payload):
    _log_request_url(method, url, params, headers)
    if str_payload != '':
        logging.info(f"Request payload: {str_payload}")


def _log_response(status_code, response, headers):
    logging.info(f"Response {status_code} {response} {headers}")


class BaseClient(object):

    def __init__(self, fiware_config: FiwareConfig):
        """Default client for making requests to FIWARE APIs

        :param fiware_config: The FiwareConfig object from which load the default configuration
        """
        # TODO Check and notify mandatory parameters on input config file
        self.fiware_config = fiware_config

        self.token = self.fiware_config.token
        self.expires_at = None

    @classmethod
    def from_config_file(cls, config_file_path):
        """Default client for making requests to FIWARE APIs

        :param config_file_path: The file in which load the default configuration
        """
        fiware_config = utils.read_config_file(config_file_path)
        return cls(fiware_config)

    @classmethod
    def from_config_json(cls, config_json: str):
        """Default client for making requests to FIWARE APIs

        :param config_json: The json string from which to load the default configuration
        """
        fiware_config = utils.parse_config_json(config_json)
        return cls(fiware_config)

    @classmethod
    def from_config_dict(cls, config_dict: dict):
        """Default client for making requests to FIWARE APIs

        :param config_dict: The config dict from which to load the default configuration
        """
        fiware_config = utils.parse_config_dict(config_dict)
        return cls(fiware_config)

    def _send_request(self, url, method, payload=None, additional_headers=None, params=None, timeout=30):
        """Auxiliary method to configure and execute a request to FIWARE APIs

        :param url: The url to be called on the request
        :param payload: The payload to be sent on the request
        :param method: The method to be used on the request
        :param additional_headers: Additional http headers to be used in the request
        :param timeout: The request's timeout
        :return: The response from the request execution
        """
        default_headers = {
            'X-Auth-Token': self.fiware_config.token,
            'Fiware-Service': self.fiware_config.service,
            'Fiware-ServicePath': self.fiware_config.service_path
        }

        additional_headers = additional_headers or {}

        headers = utils.merge_dicts(default_headers, additional_headers)

        if payload:
            if not isinstance(payload, str):
                str_payload = json.dumps(payload, indent=4)
            else:
                str_payload = payload
        else:
            str_payload = ''

        _log_request(method, url, params, headers, str_payload)

        try:
            if method == 'GET':
                r = requests.get(url, params=params, data=str_payload, headers=headers, timeout=timeout)
            elif method == 'POST':
                r = requests.post(url, params=params, data=str_payload, headers=headers, timeout=timeout)
            elif method == 'PUT':
                r = requests.put(url, params=params, data=str_payload, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                r = requests.delete(url, params=params, data=str_payload, headers=headers, timeout=timeout)
            else:
                logging.error(f"Unsupported method '{str(method)}'")
                return {'error': "Unsupported method. Select one of 'GET', 'POST', 'PUT' and 'DELETE'"}

            status_code = r.status_code
            headers = r.headers
            response_str = r.text

            try:
                response = json.loads(response_str)
            except json.decoder.JSONDecodeError as e:
                logging.error(f"Error: {e}")
                response = {}

            _log_response(status_code, response_str, headers)

            return {
                'status_code': status_code,
                'headers': headers,
                'response': response
            }

        except (ConnectionRefusedError, requests.exceptions.ConnectionError) as e:
            logging.error(f"Response Error: {e.strerror}")

            return {
                'status_code': 0,
                'response': e.strerror
            }

    def authenticate(self, username, password, timeout=30):
        """Generates an authentication token based on user credentials using FIWARE Lab OAuth2.0 Authentication system
           If you didn't have a user, go and register first at http://cloud.fiware.org

        :param username: the user's username from Fiware authentication account
        :param password: the user's password from Fiware authentication account
        :param timeout: the authentication request timeout
        :return: the generated token and expiration
        """
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

        resp = requests.post(url, data=json.dumps(payload), headers=headers, timeout=timeout)

        self.token = resp.json()["access"]["token"]["id"]
        self.expires_at = resp.json()["access"]["token"]["expires"]

        logging.debug(f"FIWARE OAuth2.0 Token: {self.token}")
        logging.debug(f"Token expiration: {self.expires_at}")

    def set_service(self, service, service_path):
        """Specify the service context to use on operations

        :param service: The name of the service to be used
        :param service_path: The service path of the service to be used
        :return: None
        """
        self.fiware_config.service = service
        self.fiware_config.service_path = service_path
