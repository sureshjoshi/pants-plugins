# pants-ty-plugin

This plugin provides a Pants `check` backend using [Ty](https://github.com/astral-sh/ty) - the new Python type checker from Astral (makers of uv and ruff).

## Installation

This plugin was tested on Python 3.11 and Pants 2.31.0.dev3.

Add the following to your `pants.toml` file:

```toml
[GLOBAL]
plugins = [
    ...
    "robotpajamas.pants.ty",
]

...

backend_packages = [
    ...
    "experimental.ty",
]
```

## Usage

This plugin is even more beta than Ty itself. It's largely just a copy/paste/rename of some existing Pants type checkers, so your mileage may vary.

`pants check --only=ty src/foo/bar.py`

The hard part of adding a new linter or formatter isn't usually the code itself, it's how to untangle the mess of configurations for the tool and weave them into various Pants-isms (e.g. configurations, interpreter constraints, partitions, environment variables, reasonable defaults, escape hatches, etc...).

## FYI

Not without some amusement, I'm unable to type check the Ty plugin itself. The pants dependencies aren't picked up, and whether this relates to some of the `namespace_packages` bugs that Ty had earlier this year, or that I've missed a configuration - I'm not sure yet. MyPy works though.
