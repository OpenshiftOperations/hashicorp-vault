#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4
'''
Custom filters for accessing HashiCorp Vault
'''

import json
import copy
import requests 

class SecretNotFoundError(Exception):
    """Exception for when a secret is not found"""

class FilterModule(object):
    '''Custom ansible filters
    
    ---
    - hosts: localhost
    gather_facts: no
    tasks:
    - import_role:
        name: openshiftoperations.hashicorp_vault
    - set_fact:
        vault_defaults:
            role_id: "{{ lookup('env','ROLE_ID') }}"
            secret_id: "{{ lookup('env','SECRET_ID') }}"
            vault_addr: "https://myvault.example.com/v1"
            mount: mysecretnamespace
    - name: store secret
        hashicorp_vault:
        mount: "{{ vault_defaults.mount }}"
        vault_addr: "{{ vault_defaults.vault_addr }}"
        role_id: "{{ vault_defaults.role_id }}"
        secret_id: "{{ vault_defaults.secret_id }}"
        name: mysecret
        data:
            foo: bar
            bar: foo
        register: mysecret
    - set_fact:
        secrets: "{{ vault_defaults | combine({'name': 'yoursecret'}) | get_secret}}"
    - debug:
        msg: "This is your secret: {{ secrets.data.yoursecret }
    '''

    def get_secret(self, fields):
        headers = {
            'X-Vault-token': self.approle_login(fields),
        }

        api_url = '/'.join([fields['vault_addr'], fields['mount'], 'data',
                           fields['name']])


        r = requests.get(api_url, headers=headers)

        if r.status_code == 404:
            raise SecretNotFoundError()


        return json.loads(r._content)['data']['data']


    def approle_login(self, login_data):
        api_url = '/'.join([login_data['vault_addr'], 'auth/approle/login'])
        r = requests.post(api_url,  data=json.dumps(login_data))

        return r.json()['auth']['client_token']
 

    def filters(self):
        ''' returns a mapping of filters to methods '''
        return {
            "get_secret": self.get_secret,
        }
