import os
from pathlib import Path

from prepare_toolbox.core import get_input, set_failed


def __display(path: Path) -> str:
    """The path as it is written in prepare.yml: relative to the working directory if it is inside it"""
    if path.is_relative_to(os.getcwd()):
        path = path.relative_to(os.getcwd())
    return path.as_posix()


def main() -> None:
    try:
        directory: str = get_input("directory")
        parents: bool = get_input("parents")
        allow_outside: bool = get_input("allow-outside-working-directory")

        path = Path(os.path.normpath(os.path.join(os.getcwd(), directory)))
        if not allow_outside and not path.is_relative_to(os.getcwd()):
            set_failed(f"The directory '{Path(directory).as_posix()}' is outside the working directory, set "
                       f"'allow-outside-working-directory' to allow this")
        try:
            path.mkdir(parents=parents, exist_ok=True)
        except FileNotFoundError:
            # Without 'parents' only the last part of the path is created, like 'mkdir' without '-p'
            missing = next(parent for parent in reversed(path.parents) if not parent.exists())
            set_failed(f"Cannot create '{Path(directory).as_posix()}': '{__display(missing)}' doesn't exist, "
                       f"set 'parents' to create the parent directories")
    except Exception as e:
        set_failed(e)


if __name__ == "__main__":
    main()
