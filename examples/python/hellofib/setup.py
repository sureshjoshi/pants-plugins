from setuptools import setup

from mypyc.build import mypycify # pants: no-infer-dep

setup(
    name="hellofib",
    packages=["hellofib"],
    ext_modules=mypycify(["hellofib/__init__.py", "hellofib/lib.py"]),
)
