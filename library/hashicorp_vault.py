#!/usr/bin/python

import requests
import urlparse
from ansible.module_utils.basic import *

''' hashicorp_vault module
    The purpose of this module is to make calls to the REST api of hashicorp
    vault

- hosts: localhost
  gather_facts: no
  tasks:
  - import_role:
      name: hashicorp_vault
  - hashicorp_vault:
      key: "foo"
      value: "bar"
      state: false
      role_id: ""
      secret_id: ""
      mount: ""
    register: secret_status 
  - debug:
      msg: "{{ item }}"
    with_items:
    - "{{secret_status.results}}"

'''

ANSIBLE_HASHI_VAULT_ADDR = 'https://vault.devshift.net/v1'


def delete_secret(fields):
    """
    Deletes secret (the value of 'name')
    """
    headers = {
        'X-Vault-token': fields['token'],
    }
    
    api_url = '/'.join([ANSIBLE_HASHI_VAULT_ADDR, fields['mount'], 'data',
        fields['name']])

    r = requests.delete(api_url, headers=headers)

    return r

    
def store_secret(fields):
    headers = {
        #'Content-Type': 'application/json',
        'X-Vault-token': fields['token'],
    }

    api_url = '/'.join([ANSIBLE_HASHI_VAULT_ADDR, fields['mount'], 'data',
        fields['name']])
    
    data = {'data':fields['data']}
    r = requests.post(api_url, headers=headers, 
                            data=json.dumps(data))

    return r

def get_secret(fields):
    headers = {
        'X-Vault-token': fields['token'],
    }
    
    api_url = '/'.join([ANSIBLE_HASHI_VAULT_ADDR, fields['mount'], 'data',
        fields['name']])

    r = requests.get(api_url, headers=headers)

    return json.loads(r._content)['data']


def approle_login(login_data):
    api_url = '/'.join([ANSIBLE_HASHI_VAULT_ADDR, 'auth/approle/login'])
    r = requests.post(api_url,  data=json.dumps(login_data))

    return r.json()['auth']['client_token']


def main():

    fields = {
        'role_id': {'type': 'str'},
        'secret_id': {'type': 'str'},
        'state': {'default': 'present', 'type': 'str'},
        'mount': { 'type': 'str'},
        'name': {'type': 'str'},
        'data': {'type': 'dict'},
    }

    module = AnsibleModule(argument_spec=fields)
    
    login_data = {
        'role_id': module.params.get('role_id'),
        'secret_id': module.params.get('secret_id')
    }

    token = approle_login(login_data)
    
    if 'data' in module.params:
        params = {
            'token': token,
            
            'mount': module.params.get('mount'),
            'name': module.params.get('name')
        }
        store_secret(params)
        results = {'value': 'success'}
    else:
        params = {
            'token': token,
            'mount': module.params.get('mount'),
            'name': module.params.get('name')
        }
        value = get_secret(params)
        results = {'value':value}
    
    module.exit_json(changed=True, results=results)


if __name__ == '__main__':
    main()