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
