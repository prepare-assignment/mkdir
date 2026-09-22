import os.path
from pathlib import Path

from prepare_toolbox.core import get_input, set_failed


def main() -> None:
    try:
        directory: str = get_input("directory")
        parents: bool = get_input("parents")
        allow_outside: bool = get_input("allow-outside-working-directory")

        path = Path(os.path.normpath(os.path.join(os.getcwd(), directory)))
        if not allow_outside and not path.is_relative_to(os.getcwd()):
            set_failed(f"The directory '{Path(directory).as_posix()}' is outside the working directory, set "
                       f"'allow-outside-working-directory' to allow this")
        path.mkdir(parents=parents, exist_ok=True)
    except Exception as e:
        set_failed(e)


if __name__ == "__main__":
    main()
