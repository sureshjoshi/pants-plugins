# pants-ansible-plugin

## How to use

In your `BUILD` file, use the new `ansible_deployment` target:
    
```python
ansible_deployment(
    name="helloansible",
    dependencies=[""],
    playbook="playbook.yml",
    #inventory="", # TODO: Could this be setup like the Docker registries? in pants.toml
    #tags="", # TODO: Might need a different name to not overlap
    #timeout="",
)
```

You can run a syntax check on your playbook via `./pants check helloansible:`

## Next Steps

1. Add support for pulling in entire Ansible deployment directory
2. Create rule for running playbook
3. Add tests
