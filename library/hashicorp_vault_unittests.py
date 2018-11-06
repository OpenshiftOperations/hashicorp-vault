#!/usr/bin/python

import unittest
import requests

from mock import patch
from hashicorp_vault import *

class TestHashicorpVault(unittest.TestCase):
    def setUp(self):
        self.fields = {
                "key": "foo",
                "value": "bar",
                "role_id": "1234",
                "secret_id": "5678",
                "mount": "secret-storage",
                "token": "abcd" 
            }


    @patch('requests.post')
    def test_store_secret(self, mock_post):
        store_secret(self.fields)
    
        headers = {
            'Content-Type': 'application/json',
            'X-Vault-token': self.fields['token'],
        }
    
        mock_post.assert_called_with(
            ANSIBLE_HASHI_VAULT_ADDR + '/secret-storage/data/foo', 
            headers=headers,
            data=json.dumps({'data':{'value': self.fields['value']}})
            )


    @patch('requests.delete')
    def test_delete_secret(self, mock_delete):
        delete_secret(self.fields)
    
        headers = {
            'X-Vault-token': self.fields['token'],
        }
    
        mock_delete.assert_called_with(
            ANSIBLE_HASHI_VAULT_ADDR + '/secret-storage/foo', 
            headers=headers,
        )


    @patch('requests.get')
    def test_get_secret(self, mock_get):
        # TypeError is expected 
        try:
            get_secret(self.fields)
        except TypeError as e:
            pass

        headers = {
            'X-Vault-token': self.fields['token'],
        }
        
        api_url = ANSIBLE_HASHI_VAULT_ADDR + '/secret-storage/foo'

        mock_get.assert_called_with(
            ANSIBLE_HASHI_VAULT_ADDR + '/secret-storage/foo', 
            headers=headers,
            )

    @patch('requests.post')
    def test_approle_login(self, mock_post):
        login_data = {
            'role_id': self.fields['role_id'],
            'secret_id': self.fields['secret_id']
        }

        # TypeError is expected 
        try: 
            approle_login(login_data)
        except TypeError as e:
            pass

        mock_post.assert_called_with(
            ANSIBLE_HASHI_VAULT_ADDR + '/auth/approle/login',
            data=json.dumps(login_data)
        )


if __name__ == '__main__':
    unittest.main()