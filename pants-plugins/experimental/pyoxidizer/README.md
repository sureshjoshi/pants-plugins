# pants-pyoxidizer-plugin

## Gameplan

1. ~~Scaffold a Pants plugin that does basically nothing~~
2. ~~Refer to Docker plugin for inspiration on how to approach PyOx~~
3. ~~Oxidize Pants emitted wheel or pex~~
4. Oxidize source through Pants python_sources

## Examples/Libraries to test

These are some typical workflows, which also highlight some unique circumstances in [PyOx's packaging](https://pyoxidizer.readthedocs.io/en/stable/pyoxidizer_packaging_additional_files.html)

1. ~~Hello World~~
2. ~~FastAPI~~ -> Installing Classified Resources on the Filesystem
3. ~~Numpy~~ -> Installing Unclassified Files on the Filesystem
4. ~~GUI~~

## Compilation Instructions

```bash
./pants --version
./pants package ::
```

## Next Steps

1. ~Take available PyOxidizer configuration or fallback to sane default~
2. Save binary to flattened dist/
3. ~Add debug and release build flags~

## Workarounds

There are some workarounds for existing libraries - which are unrelated to Pants, but specifically related to PyOxidizer.

### Missing sys.argv[0]

Some libraries require the calling filename, which PyOxidizer does not provide. While not a stable workaround, a hack could be placing this code at the top of the main module. This code is placed in the `hellokivy` and `hellotyper` examples.

```python
import sys

# Patch missing sys.argv[0] which is None for some reason when using PyOxidizer
# https://github.com/indygreg/PyOxidizer/issues/307
if sys.argv[0] is None:
    sys.argv[0] = sys.executable
    print(f"Patched sys.argv to {sys.argv}")
```
