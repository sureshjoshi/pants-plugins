# helloansible

This is a sample Ansible repo. It has many of the different pieces an Ansible repository can have:

## Collections and Roles

- "collections/ansible_collections" : local collections which don't require installation to be used
- "./my_namespace/my_collection/" : a collection which needs to be built before it can be used
- "./roles" : local roles which don't require installation to be used

## Dependencies

A top-level requirements.yml file. These files are used for playbook dependencies
Each of the collections also includes dependencies in their galaxy.yml files
The collection roles also have a dependency on the local role. Roles are also able to pull in galaxy roles, but we'd need to find a good no-op role for that. 

## Playbooks

There are several inventories, in ini and yaml formats.