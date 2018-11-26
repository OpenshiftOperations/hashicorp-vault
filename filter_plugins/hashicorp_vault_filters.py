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
            'X-Vault-token': fields['token'],
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

    def store_secret(self, fields):

        fields['token'] = self.approle_login(fields)

        headers = {'X-Vault-token': fields['token']}

        api_url = '/'.join([fields['vault_addr'], fields['mount'], 'data',
                            fields['name']])

        fdata = fields['data']
        if fdata:
            try:
                data = self.get_secret(fields)
                data.update(fdata)

            except SecretNotFoundError:
                data = fdata

            data = {'data': data}
            r = requests.post(api_url, headers=headers, 
                            data=json.dumps(data))
            return data
        else:
            try:
                return self.get_secret(fields)
            except SecretNotFoundError as e:
                raise e


    def filters(self):
        ''' returns a mapping of filters to methods '''
        return {
            "store_secret": self.store_secret,
        }
