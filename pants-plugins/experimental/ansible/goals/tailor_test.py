from experimental.ansible.goals import tailor
from experimental.ansible.goals.tailor import PutativeAnsibleTargetsRequest
from experimental.ansible.target_types import AnsibleDeployment
from pants.core.goals.tailor import AllOwnedSources, PutativeTarget, PutativeTargets
from pants.engine.rules import QueryRule
from pants.testutil.rule_runner import RuleRunner


def test_find_putative_targets() -> None:
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
        {
            "src/ansible_normal/playbook.yml": "",
            "src/ansible_more_names/named_playbook.yml": "",
            "src/ansible_file_extension/playbook.ansible": "",
        }
    )

    pts = rule_runner.request(
        PutativeTargets,
        [
            PutativeAnsibleTargetsRequest(
                (
                    "src/ansible_normal",
                    "src/ansible_more_names",
                    "src/ansible_file_extension",
                )
            ),
            AllOwnedSources(["src/ansible_normal/playbook.yml"]),
        ],
    )
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
