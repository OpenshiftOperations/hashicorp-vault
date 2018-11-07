Role Name
=========

Api wrapper for hashicorp vaults K/V version 2 secret engine.

Requirements
------------

Requests python module

Role Variables
--------------

Available variables are listed below.

    role_id
	secret_id
	mount
	name
	key
	value
	state

`role_id` and `secret_id` are variables that one should generate via vaults cli tool. These are used to get a temporary approle login token.

`mount` the mountpoint for the K/V secret.

`name` the name of the secret

`key` and `value`, K/V to put into the secret.

`state`  


Dependencies
------------

None. 

Example Playbook
----------------

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
License
-------



Author Information
------------------

This role was created in 2018 by [Liam Pieri](http://liampieri.com).