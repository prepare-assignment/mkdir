import os.path
from pathlib import Path

from prepare_toolbox.core import get_input, set_failed, info


def main() -> None:
    try:
        directory: str = get_input("directory")
        parents: bool = get_input("parents")
        path = os.path.normpath(os.path.join(os.getcwd(), directory))
        Path(path).mkdir(parents=parents, exist_ok=True)
    except Exception as e:
        set_failed(e)


if __name__ == "__main__":
    main()
