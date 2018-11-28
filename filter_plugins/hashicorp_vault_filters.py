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
    Example
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
        - set_fact:
            fields:
            role_id: "{{ hashicorp_vault_role_id }}"
            secret_id: "{{ hashicorp_vault_secret_id }}"
            vault_addr: "{{ hashicorp_vault_addr }}"
            mount: 
            name: 
            data:
                key: value 
            
        - set_fact:
            myvar: "{{ fields | store_secret}}"

        - debug:
            msg: "{{ myvar }}"    
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
