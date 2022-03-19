from experimental.cpp.lint.clangformat.rules import rules as clangformat_rules


def rules():
    return (*clangformat_rules(),)
