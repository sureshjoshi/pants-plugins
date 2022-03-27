from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Iterable, List, Protocol, Tuple

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


ansible_files = ("*.yml", "*.ansible")

def in_dir(dir: str):
    def _in_dir(dirnames: Iterable[str]) -> Tuple[str]:
        return tuple([dir + "/" + dirname for dirname in dirnames])
    return _in_dir


def ansible_dirs(dirnames: List[str]) -> Tuple[str]:
    """Source globs where we expect Ansible files. eg: 'tasks/*' TODO: Actually filter Ansible files"""
    return tuple([dirname + "/*" for dirname in dirnames])


def files_dirs(dirnames: List[str]) -> Tuple[str]:
    """Source globs where we expect any files. eg: 'files/*'"""
    return tuple([dirname + "/*" for dirname in dirnames])


plugins = "plugins/**/*"


class AnsibleSources(MultipleSourcesField, ABC):
    """All sources which Ansible will consider"""
    ...


class AnsiblePlayContext(AnsibleSources):
    default = (
        ansible_files
        + ansible_dirs(["tasks"])
        + files_dirs(["utils", "files", "templates"])
    )

    help = "Files reachable by an Ansible Play, such as tasks, templates, and files."


class AnsibleRoleSource(AnsibleSources):
    default = (
        ansible_files
        + ansible_dirs(["tasks", "handlers", "vars", "defaults", "meta"])
        + files_dirs(["library", "files", "templates"])
    )


class AnsibleCollectionSource(AnsibleSources):
    default = (
        ansible_files
        + ("readme.md", "galaxy.yml", plugins)
        + files_dirs(["docs", "meta", "plugins"])
        + in_dir("roles/*")(AnsibleRoleSource.default)
        + in_dir("playbooks")(AnsiblePlayContext.default)
    )


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
    sources: AnsiblePlayContext


class HasContext(Protocol):
    sources: AnsiblePlayContext


class RequestHasContext(Protocol):
    field_sets: Iterable[HasContext]


class AnsibleSourcesCollection(Collection[AnsibleSources]):
    ...

    @classmethod
    def from_request(cls, request: RequestHasContext) -> AnsibleSourcesCollection:
        return AnsibleSourcesCollection(
            [field_set.sources for field_set in request.field_sets]
        )
