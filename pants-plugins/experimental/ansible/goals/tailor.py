import os
from dataclasses import dataclass

from experimental.ansible.target_types import AnsibleDeployment
from pants.core.goals.tailor import (
    AllOwnedSources,
    PutativeTarget,
    PutativeTargets,
    PutativeTargetsRequest,
)
from pants.engine.fs import PathGlobs, Paths
from pants.engine.internals.selectors import Get
from pants.engine.rules import collect_rules, rule
from pants.engine.unions import UnionRule
from pants.util.logging import LogLevel


@dataclass(frozen=True)
class PutativeAnsibleTargetsRequest(PutativeTargetsRequest): ...


@rule(level=LogLevel.INFO, desc="Determine candidate Ansible playbook targets to create")
async def find_putative_targets(
    req: PutativeAnsibleTargetsRequest, all_owned_sources: AllOwnedSources
) -> PutativeTargets:
    playbooks = await Get(
        Paths,
        PathGlobs,
        req.path_globs("*playbook*.yml", "*playbook*.yml", "*playbook*.ansible"),
    )

    unowned_playbooks = set(playbooks.files) - set(all_owned_sources)
    return PutativeTargets([playbook_to_target(playbook) for playbook in sorted(unowned_playbooks)])


def playbook_to_target(playbook: str) -> PutativeTarget:
    dirname, filename = os.path.split(playbook)
    kwargs = {"playbook": filename}
    # TODO: This doesn't populate the playbook field, and causes a runtime failure
    # if filename != AnsiblePlaybook.default:
    #   kwargs["playbook"] = filename
    return PutativeTarget.for_target_type(
        AnsibleDeployment,
        path=dirname,
        name="ansible_playbook",
        triggering_sources=[filename],
        kwargs=kwargs,
    )


def rules():
    return [
        *collect_rules(),
        UnionRule(PutativeTargetsRequest, PutativeAnsibleTargetsRequest),
    ]
