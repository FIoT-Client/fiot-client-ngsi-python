import configparser
import json

import requests


class SimpleClient:

    def __init__(self):
        config_file = "config.ini"

        # Load the default configuration file
        with open(config_file, 'r+') as f:
            sample_config = f.read()
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_string(sample_config)

        self.fiware_service = config.get('service', 'fiware-service')
        self.fiware_service_path = config.get('service', 'fiware-service-path')

        self.idas_aaa = config.get('idas', 'OAuth')  # TODO Mode to correct place
        if self.idas_aaa == "yes":
            self.token = config.get('user', 'token')
            self.token_show = self.token[1:5] + "*" * 70 + self.token[-5:]
        else:
            self.token = "NULL"
            self.token_show = "NULL"

        self.host_id = config.get('local', 'host_id')

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

        tokens_url = "http://cloud.lab.fi-ware.org:4730/v2.0/tokens"

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

    def set_service(self, service, service_path):
        self.fiware_service = service
        self.fiware_service_path = service_path
