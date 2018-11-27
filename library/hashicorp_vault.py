#!/usr/bin/python

import requests

from ansible.module_utils.basic import json, AnsibleModule

''' hashicorp_vault module
    The purpose of this module is to make calls to the REST api of hashicorp
    vault
---
---
- hosts: localhost
  gather_facts: no
  vars:
    hashicorp_vault_role_id: 
    hashicorp_vault_secret_id: 
    hashicorp_vault_addr: 

  tasks:
    - name: Run the hashicorp_vault role
      import_role:
        name: liamwazherealso.openshift_hashicorp_vault
    - name: Check secrets
      hashicorp_vault:
        role_id: "{{ hashicorp_vault_role_id }}"
        secret_id: "{{ hashicorp_vault_secret_id }}"
        vault_addr: "{{ hashicorp_vault_addr }}"
        mount: 
        name: 
        data: 
          key: value
        
      register: secret_status

    - name: View secret results
      debug:
        msg: "{{ item }}"
      loop:
        - "{{secret_status.results}}"
      
'''

class SecretNotFoundError(Exception):
    """Exception for when a secret is not found"""

    
def store_secret(fields):
    headers = {'X-Vault-token': fields['token']}

    api_url = '/'.join([fields['vault_addr'], fields['mount'], 'data',
                        fields['name']])

    if 'data' in fields:
        fdata = fields['data'] 
        try:
            data = get_secret(fields)
            data.update(fdata)

        except SecretNotFoundError:
            data = fdata

        data = {'data': data}
        r = requests.post(api_url, headers=headers, 
                        data=json.dumps(data))
        return data
    else:
        return {'data': get_secret(fields)}


def get_secret(fields):
    headers = {
        'X-Vault-token': fields['token'],
    }

    api_url = '/'.join([fields['vault_addr'], fields['mount'], 'data',
                       fields['name']])


    r = requests.get(api_url, headers=headers)

    if r.status_code == 404:
        raise SecretNotFoundError()


    return json.loads(r._content)['data']['data']


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
    
    data = module.params.get('data')

    if data:
        params = {
            'vault_addr': vault_addr,
            'token': token,
            'mount': module.params.get('mount'),
            'name': module.params.get('name'),
            'data': data
        }
        store_secret(params)
        results = {'data': data}
    else:
        params = {
            'vault_addr': vault_addr,
            'token': token,
            'mount': module.params.get('mount'),
            'name': module.params.get('name')
        }
        results = {'data':  get_secret(params)}
    
    module.exit_json(changed=True, results=results)


if __name__ == '__main__':
    main()
