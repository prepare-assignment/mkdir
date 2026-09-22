import json
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml
from pytest_mock import MockerFixture

from prepare_mkdir.main import main

TASK = Path(__file__).parent.parent / "task.yml"


def set_inputs(monkeypatch: pytest.MonkeyPatch, **inputs: Any) -> None:
    """
    Pass the inputs like prepare-assignment core does: as JSON in PREPARE_<NAME> environment variables,
    including the defaults from task.yml. Use the names from task.yml, with '_' for '-'.
    """
    definition: Dict[str, Any] = yaml.safe_load(TASK.read_text(encoding="utf-8"))["inputs"]
    values = {name: spec["default"] for name, spec in definition.items() if "default" in spec}
    values.update({key.replace("_", "-"): value for key, value in inputs.items()})
    for key, value in values.items():
        if value is not None:
            monkeypatch.setenv(f"PREPARE_{key.upper()}", json.dumps(value))


@pytest.fixture
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    project
    |- test.txt
    |- out
    """
    (tmp_path / "out").mkdir()
    (tmp_path / "test.txt").write_text("test.txt")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_create(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    set_inputs(monkeypatch, directory="assignment")
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_not_called()
    assert (project / "assignment").is_dir()


def test_create_in_existing_directory(project: Path, monkeypatch: pytest.MonkeyPatch,
                                      mocker: MockerFixture) -> None:
    set_inputs(monkeypatch, directory="out/images")
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_not_called()
    assert (project / "out" / "images").is_dir()


def test_parents(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    set_inputs(monkeypatch, directory="out/images/icons", parents=True)
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_not_called()
    assert (project / "out" / "images" / "icons").is_dir()


def test_missing_parent(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    """Without 'parents' only the last part of the path is created, like 'mkdir' without '-p'"""
    set_inputs(monkeypatch, directory="out/images/icons")
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_called_once()
    assert not (project / "out" / "images").exists()


def test_existing_directory(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    """An existing directory is not an error: the task can run again without failing"""
    set_inputs(monkeypatch, directory="out")
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_not_called()
    assert (project / "out").is_dir()


def test_existing_file(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    set_inputs(monkeypatch, directory="test.txt")
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_called_once()
    assert (project / "test.txt").read_text() == "test.txt"


def test_absolute_path(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    set_inputs(monkeypatch, directory=str(project / "out" / "images"))
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_not_called()
    assert (project / "out" / "images").is_dir()
