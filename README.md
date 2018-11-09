Role Name
=========

API wrapper to manage secrets in Hashicorp Vault's K/V version 2 secret engine.

Requirements
------------

Python `requests`

Role Variables
--------------

`vault_addr`: Vault server address

`role_id`, `secret_id`: AppRole auth credentials. See [documentation](https://www.vaultproject.io/docs/auth/approle.html) for details on AppRole auth.

`mount`: The mount point for the K/V secret.

`name`: secret name.

`data`: { `key`: `value` }: K/V data

Dependencies
------------

None.

Example Playbook
----------------

Store new or update existing secret with KV pair.

```
---
- hosts: localhost
  gather_facts: no
  tasks:
  - import_role:
      name: liamwazherealso.openshift_hashicorp_vault
  - name: store secret
    hashicorp_vault:
      mount: secret
      name: mysecret
      data:
        foo: bar
      vault_addr: "https://vault-server.com"
      role_id: "{{ lookup('env','ROLE_ID') }}"
      secret_id: "{{ lookup('env','SECRET_ID') }}"
    register: mysecret
  - debug:
    msg: "{{ mysecret.results }}"
```

License
-------

Apache 2.0

Author Information
------------------

This role was created in 2018 by [Liam Pieri](http://liampieri.com).
