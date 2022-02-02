from experimental.mypyc.rules import rules as mypyc_rules
from experimental.mypyc.target_types import MyPycPythonDistribution


def rules():
    return (*mypyc_rules(),)


def target_types():
    return (MyPycPythonDistribution,)
