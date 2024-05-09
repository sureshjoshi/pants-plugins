# Copyright 2024 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import libcst
import libcst.matchers as m
from experimental.migrate.subsystems import Migrate, MigrateSubsystem
from libcst import RemovalSentinel, RemoveFromParent
from pants.engine.console import Console
from pants.engine.rules import Rule, collect_rules, goal_rule
from pants.engine.target import UnexpandedTargets


class RemoveRuleTransformer(m.MatcherDecoratableTransformer):
    @m.leave(
        m.ImportFrom(
            module=m.DoNotCare(),
            names=[
                m.ZeroOrMore(),
                m.ImportAlias(name=m.Name("rule_helper")),
                m.ZeroOrMore(),
            ],
        )
    )
    def handle_imports(
        self, original_node: libcst.ImportFrom, updated_node: libcst.ImportFrom
    ) -> libcst.ImportFrom | RemovalSentinel:
        assert not isinstance(original_node.names, libcst.ImportStar)

        if len(original_node.names) == 1:
            return RemoveFromParent()

        return updated_node.with_changes(
            names=[n for n in original_node.names if n.evaluated_name != "rule_helper"],
            # This is a workaround for https://github.com/Instagram/LibCST/issues/532
            # Formatters/isort will clean this up, but it doesn't compile without this
            lpar=libcst.LeftParen(),
            rpar=libcst.RightParen(),
        )

    @m.leave(m.Decorator(decorator=m.Name("rule_helper")))
    def handle_decorator(
        self, original_node: libcst.Decorator, updated_node: libcst.Decorator
    ) -> libcst.Decorator | RemovalSentinel:
        return RemoveFromParent()


# TODO: This will need to become a BuiltinGoal, so just hacking around to get a list of Targets
# Normally, will use the same code for "call-by-name-migration"
@goal_rule
async def migrate(
    console: Console, subsystem: MigrateSubsystem, targets: UnexpandedTargets
) -> Migrate:
    filenames = [t.address.filename for t in targets if t.address.is_file_target]

    for f in sorted(filenames):
        file = Path(f)
        if file.suffix != ".py":
            continue
        with open(file) as f:
            source = f.read()
            tree = libcst.parse_module(source)
            new_tree = tree.visit(RemoveRuleTransformer())
            new_source = new_tree.code

            if source != new_source:
                console.print_stderr(f"Rewriting {file}")
                with open(file, "w") as f:
                    f.write(new_source)

    return Migrate(exit_code=0)


def rules() -> Iterable[Rule]:
    return collect_rules()
