#!/usr/bin/python
# -*- coding: utf-8 -*-
# vim: expandtab:tabstop=4:shiftwidth=4
'''
Custom filters for accessing HashiCorp Vault
'''

import requests 

class FilterModule(object):
    '''Custom ansible filters'''

    @staticmethod
    def approle_login(login_data):
        api_url = '/'.join([login_data['vault_addr'], 'auth/approle/login'])
        r = requests.post(api_url,  data=json.dumps(login_data))

        return r.json()['auth']['client_token']

    @staticmethod
    def store_secret(fields):

        fields['token'] = approle_login(fields)

        headers = {'X-Vault-token': fields['token']}

        api_url = '/'.join([fields['vault_addr'], fields['mount'], 'data',
                            fields['name']])
        
        data = {'data': fields['data']}

        try:
            data.update(get_secret(fields)['data'])
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
