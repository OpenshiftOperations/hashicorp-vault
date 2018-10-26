#!/usr/bin/python

import requests
import urlparse
from ansible.module_utils.basic import *

ANSIBLE_HASHI_VAULT_ADDR = 'http://127.0.0.1:8200'

if os.getenv('VAULT_ADDR') is not None:
    ANSIBLE_HASHI_VAULT_ADDR = os.environ['VAULT_ADDR']

def store_secret(fields):
    header = {
        'Content-Type': 'application/json',
        'X-Vault-token': fields['token'],
    }
    
    data = {'value': fields['value']}

    api_url = urlparse.urljoin(ANSIBLE_HASHI_VAULT_ADDR, fields['mount'], 
        fields['key'])
    r = requests.post(api_url, header=header, data=data)

def get_secret(fields):
    header = {
        'X-Vault-token': fields['token'],
    }
    
    api_url = urlparse.urljoin(ANSIBLE_HASHI_VAULT_ADDR, fields['mount'], 
        fields['key'])

    r = requests.get(api_url, header=header)

def approle_login(login_data):
    api_url = urlparse.urljoin(ANSIBLE_HASHI_VAULT_ADDR, 'auth/approle/login')
    r = requests.post(api_url, data=login_data)
    token = r.json()['client_token']

    return token


def main():

    fields = {
        "key": {"default": True, "type": "str"},
        "value": {"default": True, "type": "str"},
        "present": {"default": True, "type": "bool"},
        "role_id": {"default": True, "type": "str"},
        "secret_id": {"default": True, "type": "str"},
        "mount": {"default": True, "type": "str"}
    }

    module = AnsibleModule(argument_spec=fields)
    
    login_data = {
        "role_id": fields['role_id'],
        "secret_id": fields['secret_id']
    }

    fields['token'] = approle_login(login_data)

    if fields['present']:
        get_secret(fields)
    else:
        store_secret(fields)

    module.exit_json(changed=True, meta=module.params)


if __name__ == '__main__':
    main()