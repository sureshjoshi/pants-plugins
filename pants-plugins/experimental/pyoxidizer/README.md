# pants-pyoxidizer-plugin

# [Mainlined in 2.10](https://www.pantsbuild.org/v2.10/docs/pyoxidizer) via [PR #14183](https://github.com/pantsbuild/pants/pull/14183)

## Resources

- [Official docs](https://www.pantsbuild.org/v2.10/docs/pyoxidizer)
- My [Packaging Python with the PyOxidizer Pants Plugin](https://blog.pantsbuild.org/packaging-python-with-the-pyoxidizer-pants-plugin/) blog post

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
