#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4
'''
Custom filters for accessing HashiCorp Vault
'''

import json
import requests 

class SecretNotFoundError(Exception):
    """Exception for when a secret is not found"""

class FilterModule(object):
    '''Custom ansible filters'''

    def get_secret(self, fields):
        headers = {
            'X-Vault-token': fields['token'],
        }

        api_url = '/'.join([fields['vault_addr'], fields['mount'], 'data',
                           fields['name']])


        r = requests.get(api_url, headers=headers)

        if r.status_code == 404:
            raise SecretNotFoundError()


        return json.loads(r._content)['data']


    def approle_login(self, login_data):
        api_url = '/'.join([login_data['vault_addr'], 'auth/approle/login'])
        r = requests.post(api_url,  data=json.dumps(login_data))

        return r.json()['auth']['client_token']

    def store_secret(self, fields):

        fields['token'] = self.approle_login(fields)

        headers = {'X-Vault-token': fields['token']}

        api_url = '/'.join([fields['vault_addr'], fields['mount'], 'data',
                            fields['name']])
        
        data = {'data': fields['data']}

        try:
            data['data'].update(self.get_secret(fields)['data'])
        except SecretNotFoundError:
            pass

        r = requests.post(api_url, headers=headers, 
                        data=json.dumps(data))

        return r.status_code

    def filters(self):
        ''' returns a mapping of filters to methods '''
        return {
            "store_secret": self.store_secret,
        }
