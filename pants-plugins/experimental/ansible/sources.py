from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from experimental.ansible.deploy import DeploymentFieldSet
from experimental.ansible.target_types import (
    AnsibleDependenciesField,
    AnsiblePlaybook,
    AnsiblePlayContext,
)
from pants.engine.collection import Collection
from pants.engine.fs import Digest


@dataclass(frozen=True)
class AnsibleSourcesDigest:
    digest: Digest


@dataclass(frozen=True)
class AnsibleFieldSet(DeploymentFieldSet):
    required_fields = (
        AnsibleDependenciesField,
        AnsiblePlaybook,
        AnsiblePlayContext,
    )

    dependencies: AnsibleDependenciesField
    playbook: AnsiblePlaybook
    ansiblecontext: AnsiblePlayContext


class HasContext(Protocol):
    ansiblecontext: AnsiblePlayContext


class RequestHasContext(Protocol):
    field_sets: Iterable[HasContext]


class AnsibleContexts(Collection[AnsiblePlayContext]):
    ...

    @classmethod
    def from_request(cls, request: RequestHasContext) -> AnsibleContexts:
        return AnsibleContexts(
            [field_set.ansiblecontext for field_set in request.field_sets]
        )
