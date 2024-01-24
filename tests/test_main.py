import json
import os
import pytest
from pathlib import Path

from pytest_mock import MockerFixture

from mkdir.main import main


def set_environment(directory: str, parents: bool = False) -> None:
    os.environ["PREPARE_DIRECTORY"] = json.dumps(directory)
    os.environ["PREPARE_PARENTS"] = json.dumps(parents)


@pytest.mark.parametrize(
    "directory, parents", [
        ("out", False),
        ("out", True),
        ("out/images", True)
    ]
)
def test_mkdir(directory: str, parents: bool, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    set_environment(directory, parents)
    main()
    assert os.path.isdir(os.path.join(tmp_path, directory))


def test_absolute(tmp_path: Path) -> None:
    directory = os.path.join(tmp_path, "out")
    set_environment(directory)
    main()
    assert os.path.isdir(directory)


def test_parents_not_set(tmp_path: Path, mocker: MockerFixture) -> None:
    directory = os.path.join(tmp_path, "out/images")
    set_environment(directory)
    spy = mocker.patch("mkdir.main.set_failed")
    main()
    spy.assert_called_once()
