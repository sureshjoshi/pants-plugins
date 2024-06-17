# pants-plugin

A small selection of custom PantsBuild plugins.

## Usage

Install Pants via [PantsBuild's instructions](https://www.pantsbuild.org/docs/installation), or use `brew` via `brew install pantsbuild/tap/pants`.

## Plugins

- [ansible](https://github.com/sureshjoshi/pants-plugins/blob/main/pants-plugins/experimental/ansible/README.md)
- ClangFormat - Mainlined via [PR #15395](https://github.com/pantsbuild/pants/pull/15395)
- [mypyc](https://github.com/sureshjoshi/pants-plugins/blob/main/pants-plugins/experimental/mypyc/README.md) - Similar solution mainlined in 2.13 via [PR #15380](https://github.com/pantsbuild/pants/pull/15380)
- nodejs - Mainlined via [PR #15442](https://github.com/pantsbuild/pants/pull/15442)
- Prettier - Mainlined via [PR #15480](https://github.com/pantsbuild/pants/pull/15480)
- [PyOxidizer](https://www.pantsbuild.org/v2.10/docs/pyoxidizer) - Mainlined in 2.10 via [PR #14183](https://github.com/pantsbuild/pants/pull/14183)
    - My [Packaging Python with the PyOxidizer Pants Plugin](https://blog.pantsbuild.org/packaging-python-with-the-pyoxidizer-pants-plugin/) blog post
    - Examples removed from repo as of May 20, 2023 (last commit with examples: [ea2b275](https://github.com/sureshjoshi/pants-plugins/commit/ea2b2755e6d1ffc8b3222f0b03a222a036f1e65a))
    - [Issue #90](https://github.com/sureshjoshi/pants-plugins/issues/90) for rationale
- [scie](https://github.com/sureshjoshi/pants-plugins/blob/main/pants-plugins/experimental/scie/README.md)

## VS Code Configuration

In order to get intellisense working correctly in VS Code, here are the relevant items to look at:

### pants.toml

Ensure the following:

- `pants.backend.plugin_development` setup inside `backend_packages`
- There is a separate resolve for your plugin directory, matching the Pants required interpreter (3.9 right now)

```toml
backend_packages = [
    "pants.backend.plugin_development",
    ...
]

[python]
enable_resolves = true
interpreter_constraints = ["==3.9.*"]
tailor_pex_binary_targets = false

[python.resolves]
pants-plugins = "build-support/lockfiles/pants-plugins.lock"
python-default = "build-support/lockfiles/python-default.lock"

[python.resolves_to_interpreter_constraints]
pants-plugins = [">=3.9,<3.10"]
```

### requirements

In the plugin root folder, there is a BUILD file containing the following (where the resolve is the same name that you setup in pants.toml):

```python
pants_requirements(name="pants", resolve="pants-plugins")
```

### .vscode/settings.json

In the past, this setting appears to help the VS Code intellisense auto-complete.

```json
{
  "python.analysis.packageIndexDepths": [
    { "name": "pants", "depth": 5, "includeAllSymbols": true }
  ]
} 
```

### venv

Generate the lockfile (very important if `pants_version` changes, so you're using the updated pants wheel). Then, export the resolve and setup VS Code to use that venv.

```bash
pants generate-lockfiles --resolve=pants-plugins # This is important if you've upgraded your pants version
pants export --resolve=pants-plugins

# Use this venv in VS Code 
Wrote mutable virtualenv for pants-plugins (using Python 3.9.19) to dist/export/python/virtualenvs/pants-plugins/3.9.19
```

You can also symlink the exported directory to `.venv` or similar, as VS Code tends to automatically pick those up. 

Important: Do not activate the `venv` and run commands, or you'll get a complaint about using the `pants launcher binary`.
