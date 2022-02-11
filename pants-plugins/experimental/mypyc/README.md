# pants-mypyc-plugin

## How to use

1. This plugin requires changes to the Pants source code, so you'll need to use the [pants_from_sources](https://www.pantsbuild.org/docs/running-pants-from-sources#running-pants-from-sources-in-other-repos) approach against https://github.com/sureshjoshi/pants/tree/mypyc-support

2. Add `mypyc` support to the setuptools process:

    ```toml
    # pants.toml
    [setuptools]
    extra_requirements = ["wheel", "mypy"]
    lockfile = "build-support/setuptools.txt"
    ```

3. In your `BUILD` file, use the new `mypyc_python_distribution` target (which is identical to `python_distribution` with a new name)
    ```python
    mypyc_python_distribution(
        name="hellofib-dist",
        dependencies=[":libhellofib"],
        wheel=True,
        sdist=False,
        provides=setup_py(
            name="hellofib-dist",
            version="0.0.1",
            description="A distribution for the hello fib library.",
        ),
        # Setting this True or False depends on the next step
        generate_setup = True,
    )
    ```

4. If you want to test using your own `setup.py`, place one in your source root and set `generate_setup = False` in the `BUILD` file
    ```python
    # setup.py
    from setuptools import setup

    from mypyc.build import mypycify

    setup(
        name="hellofib",
        packages=["hellofib"],
        ext_modules=mypycify(
            [
                "hellofib/__init__.py",
                "hellofib/main.py",
            ]
        ),
    )
    ```

5. If you want the plugin to auto-generate your `setup.py`, set `generate_setup = True` in the `BUILD` file (or remove the line, since `True` is the default). The plugin will pass all of the source files from the dependencies into `mypycify`

## Examples/Libraries to test

All of the examples that can compile with `mypyc_python_distribution` have that target applied. There are some outstanding examples which fail when `mypy` tries to compile them.

To quickly see which examples are supported, type the following: `./pants_from_sources filter --target-type=mypyc_python_distribution ::`

For example, with `hellofib`:
```bash
./pants_from_sources --version
./pants_from_sources package hellofib:hellofib-dist

pip install dist/hellofib-{whatever}-.whl --force-reinstall
python -c "from hellofib.main import main; main()"
```

## Next Steps

1. Add support for multiple dependency targets (only tested/working with one `python_sources` dependency)
2. Handle use case where `ext_modules` are already specified in the SetupKwargs
3. Figure out better API for SetupPyContentRequest - it feels a bit hacky to expect a certain key from another method, where there might be a better, more holistic solution
4. ~Test on imported libraries and add libraries to pants deps~
