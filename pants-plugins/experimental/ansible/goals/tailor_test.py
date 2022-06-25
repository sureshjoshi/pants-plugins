import os

from experimental.ansible.goals import tailor
from experimental.ansible.goals.tailor import PutativeAnsibleTargetsRequest
from experimental.ansible.target_types import AnsibleDeployment
from pants.core.goals.tailor import AllOwnedSources, PutativeTarget, PutativeTargets
from pants.engine.rules import QueryRule
from pants.testutil.rule_runner import RuleRunner

FileInfos = tuple[tuple[str, str], ...]


def run_tailor(files: FileInfos, owned: FileInfos) -> PutativeTargets:
    rule_runner = RuleRunner(
        rules=[
            *tailor.rules(),
            QueryRule(
                PutativeTargets, [PutativeAnsibleTargetsRequest, AllOwnedSources]
            ),
        ],
        target_types=[AnsibleDeployment],
    )

    rule_runner.write_files(
        {os.path.join(directory, fname): "" for directory, fname in files}
    )

    pts = rule_runner.request(
        PutativeTargets,
        [
            PutativeAnsibleTargetsRequest(tuple(directory for directory, _ in files)),
            AllOwnedSources(
                [os.path.join(directory, fname) for directory, fname in owned]
            ),
        ],
    )
    return pts


def test_find_putative_targets() -> None:
    files = (
        ("src/ansible_normal", "playbook.yml"),
        ("src/ansible_more_names", "named_playbook.yml"),
        ("src/ansible_file_extension", "playbook.ansible"),
    )

    pts = run_tailor(files, (files[0],))

    assert pts == (
        PutativeTargets(
            [
                PutativeTarget.for_target_type(
                    AnsibleDeployment,
                    path="src/ansible_more_names",
                    name="ansible_playbook",
                    triggering_sources=["named_playbook.yml"],
                    kwargs={"playbook": "named_playbook.yml"},
                ),
                PutativeTarget.for_target_type(
                    AnsibleDeployment,
                    path="src/ansible_file_extension",
                    name="ansible_playbook",
                    triggering_sources=["playbook.ansible"],
                    kwargs={"playbook": "playbook.ansible"},
                ),
            ]
        )
    )


def test_find_normal_name() -> None:
    files = (("src/ansible", "playbook.yml"),)
    pts = run_tailor(files, tuple())
    assert pts == (
        PutativeTargets(
            [
                PutativeTarget.for_target_type(
                    AnsibleDeployment,
                    path=files[0][0],
                    name="ansible_playbook",
                    triggering_sources=[files[0][1]],
                ),
            ]
        )
    )


def test_find_extended_name() -> None:
    files = (("src/ansible", "extended_playbook.yml"),)
    pts = run_tailor(files, tuple())
    assert pts == (
        PutativeTargets(
            [
                PutativeTarget.for_target_type(
                    AnsibleDeployment,
                    path=files[0][0],
                    name="ansible_playbook",
                    triggering_sources=[files[0][1]],
                    kwargs={
                        "playbook": files[0][1]
                    },  # assert that the playbook field is set
                ),
            ]
        )
    )


def test_find_alternate_extension() -> None:
    """the `.ansible` extension helps with syntax highlighters as `.yml` often isn't picked up"""
    files = (("src/ansible", "playbook.ansible"),)
    pts = run_tailor(files, tuple())
    assert pts == (
        PutativeTargets(
            [
                PutativeTarget.for_target_type(
                    AnsibleDeployment,
                    path=files[0][0],
                    name="ansible_playbook",
                    triggering_sources=[files[0][1]],
                    kwargs={
                        "playbook": files[0][1]
                    },  # assert that the playbook field is set
                ),
            ]
        )
    )


def test_ignore_owned_sources() -> None:
    files = (("src/ansible", "playbook.ansible"),)
    pts = run_tailor(files, files)
    assert pts == (PutativeTargets([]))
