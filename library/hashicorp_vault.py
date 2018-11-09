#!/usr/bin/python

import requests

from ansible.module_utils.basic import json, AnsibleModule

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
      role_id: ""
      secret_id: ""
      mount: ""
    register: secret_status 
  - debug:
      msg: "{{ item }}"
    with_items:
    - "{{secret_status.results}}"

'''


def delete_secret(fields):
    """
    Deletes secret (the value of 'name')
    """
    headers = {
        'X-Vault-token': fields['token'],
    }
    
    api_url = '/'.join([fields['vault_addr'], fields['mount'], 'data',
                        fields['name']])

    r = requests.delete(api_url, headers=headers)

    return r

    
def store_secret(fields):
    headers = {'X-Vault-token': fields['token']}

    api_url = '/'.join([fields['vault_addr'], fields['mount'], 'data',
                        fields['name']])
    
    data = {'data':fields['data']}
    r = requests.post(api_url, headers=headers, 
                      data=json.dumps(data))

    return r


def get_secret(fields):
    headers = {
        'X-Vault-token': fields['token'],
    }
    
    api_url = '/'.join([fields['vault_addr'], fields['mount'], 'data',
                       fields['name']])

    r = requests.get(api_url, headers=headers)

    return json.loads(r._content)['data']


def approle_login(login_data):
    api_url = '/'.join([login_data['vault_addr'], 'auth/approle/login'])
    r = requests.post(api_url,  data=json.dumps(login_data))

    return r.json()['auth']['client_token']


def main():

    fields = {
        'role_id': {'type': 'str'},
        'secret_id': {'type': 'str'},
        'mount': {'type': 'str'},
        'name': {'type': 'str'},
        'vault_addr': {'type': 'str'},
        'data': {'type': 'dict'}
    }

    module = AnsibleModule(argument_spec=fields)
    
    vault_addr = module.params.get('vault_addr')

    login_data = {
        'vault_addr': vault_addr,
        'role_id': module.params.get('role_id'),
        'secret_id': module.params.get('secret_id')
    }

    token = approle_login(login_data)
    
    if 'data' in module.params:
        params = {
            'vault_addr': vault_addr,
            'token': token,
            'mount': module.params.get('mount'),
            'name': module.params.get('name')
        }
        store_secret(params)
        results = {'value': 'success'}
    else:
        params = {
            'vault': vault_addr,
            'token': token,
            'mount': module.params.get('mount'),
            'name': module.params.get('name')
        }
        value = get_secret(params)
        results = {'value': value}
    
    module.exit_json(changed=True, results=results)


if __name__ == '__main__':
    main()