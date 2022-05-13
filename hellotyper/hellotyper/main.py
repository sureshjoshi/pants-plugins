import sys

# Patch missing sys.argv[0] which is None for some reason when using PyOxidizer
# Typer fails on this because it tries to emit the filename
if sys.argv[0] is None:
    sys.argv[0] = sys.executable
    print(f"Patched sys.argv to {sys.argv}")

# pylint: disable=wrong-import-position
import typer


def main(name: str):
    typer.echo(f"Hello {name}")


if __name__ == "__main__":
    typer.run(main)
