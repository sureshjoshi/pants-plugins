from experimental.nodejs.target_types import (
    NodeSourcesGeneratorTarget,
    NodeSourceTarget,
)


def target_types():
    return (
        NodeSourceTarget,
        NodeSourcesGeneratorTarget,
    )
