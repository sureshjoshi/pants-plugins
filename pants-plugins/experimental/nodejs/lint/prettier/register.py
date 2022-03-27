from experimental.nodejs.lint.prettier.rules import rules as prettier_rules


def rules():
    return (*prettier_rules(),)
