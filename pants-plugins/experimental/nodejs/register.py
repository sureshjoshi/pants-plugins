from experimental.nodejs.rules import rules as nodejs_rules
from experimental.nodejs.target_types import (
    NodeSourcesGeneratorTarget,
    NodeSourceTarget,
)


def rules():
    return (*nodejs_rules(),)


def target_types():
    return (
        NodeSourceTarget,
        NodeSourcesGeneratorTarget,
    )
