from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from experimental.ansible.deploy import DeploymentFieldSet
from pants.engine.collection import Collection
from pants.engine.fs import Digest
from pants.engine.target import Dependencies, MultipleSourcesField, SingleSourceField


class AnsibleDependenciesField(Dependencies):
    pass


class AnsiblePlaybook(SingleSourceField):
    alias = "playbook"
    default = "playbook.yml"
    help = (
        "The .yml file to use when running ansible-playbook.\n\n"
        "Path is relative to the BUILD file's directory, e.g. `playbook='playbook.yml'`."
    )


class AnsiblePlayContext(MultipleSourcesField):
    alias = "ansiblecontext"
    default = (
        "*.yml",
        "*.ansible",
        "files/*",
        "tasks/*",
        "templates/*",
        "utils/*",
    )
    help = "Files reachable by an Ansible Play, such as tasks, templates, and files."


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
