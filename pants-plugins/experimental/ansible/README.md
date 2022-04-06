# pants-ansible-plugin

## How to use

In your `BUILD` file, use the new `ansible_sources` to pull in the entire target directory and `ansible_deployment` to support the new `./pants deploy` goal:
    
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

In `pants.toml`, you can setup your Ansible Galaxy collection installations:

```toml
[ansible-galaxy]
requirements = "requirements.yml" # Relative to the Ansible target BUILD
collections = ["community.docker"]
```

## Next Steps

1. Add tests
