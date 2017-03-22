import requests
import json


def get_token(keystone_url):
    print('getting token...')

    json_payload = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": "idm",
                        "domain": {"id": "default"},
                        "password": "idm"
                    }
                }
            }
        }
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(url=keystone_url + '/v3/auth/tokens',
                             data=json.dumps(json_payload),
                             headers=headers)

    if response.status_code in (201, 200):
        token = response.headers['X-Subject-Token']
        print('TOKEN --- ' + token)
        return token
    else:
        print('GET TOKEN ### ' + response.text)

if __name__ == "__main__":
    keystone_url = "http://192.168.99.100:5000"
    token = get_token(keystone_url)
