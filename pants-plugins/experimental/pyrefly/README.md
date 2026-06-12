# pants-pyrefly-plugin

This plugin provides a Pants `check` backend using [Pyrefly](https://github.com/facebook/pyrefly) - the new Python type checker from Facebook.

## Installation

This plugin was tested on Python 3.11+ and Pants 2.33.0.dev3 and 2.32.0.

The plugin ships Pyrefly **1.0.0** from the [official GitHub releases](https://github.com/facebook/pyrefly/releases). Pants automatically passes your configured `[source].root_patterns` to Pyrefly as `--search-path`, so you typically do not need a `search-path` entry in `[tool.pyrefly]`.

Add the following to your `pants.toml` file:

```toml
[GLOBAL]
plugins = [
    ...
    "robotpajamas.pants.pyrefly",
]

...

backend_packages = [
    ...
    "experimental.pyrefly",
]
```

## Usage

This plugin is  even more beta than Pyrefly itself. It's largely just a copy/paste/rename of the [Ty plugin](https://pypi.org/project/robotpajamas.pants.ty/), so your mileage may vary.

`pants check --only=pyrefly src/foo/bar.py`

The hard part of adding a new linter or formatter isn't usually the code itself, it's how to untangle the mess of configurations for the tool and weave them into various Pants-isms (e.g. configurations, interpreter constraints, partitions, environment variables, reasonable defaults, escape hatches, etc...).
