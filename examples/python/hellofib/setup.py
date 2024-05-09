from mypyc.build import mypycify  # pants: no-infer-dep
from setuptools import setup

setup(
    name="hellofib",
    packages=["hellofib"],
    ext_modules=mypycify(["hellofib/__init__.py", "hellofib/lib.py"]),
)
