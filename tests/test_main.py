import json
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml
from pytest_mock import MockerFixture

import prepare_mkdir.main as mkdir_main
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


def created(set_output: Any) -> str:
    """The directory output, as is: paths use '/' on every platform (they are used in other steps)"""
    set_output.assert_called_once()
    return str(set_output.call_args.args[1])


def test_create(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    set_inputs(monkeypatch, directory="assignment")
    set_output = mocker.patch("prepare_mkdir.main.set_output")
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_not_called()
    assert (project / "assignment").is_dir()
    assert created(set_output) == "assignment"


def test_create_in_existing_directory(project: Path, monkeypatch: pytest.MonkeyPatch,
                                      mocker: MockerFixture) -> None:
    set_inputs(monkeypatch, directory="out/images")
    set_output = mocker.patch("prepare_mkdir.main.set_output")
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_not_called()
    assert (project / "out" / "images").is_dir()
    assert created(set_output) == "out/images"


def test_parents(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    set_inputs(monkeypatch, directory="out/images/icons", parents=True)
    set_output = mocker.patch("prepare_mkdir.main.set_output")
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_not_called()
    assert (project / "out" / "images" / "icons").is_dir()
    assert created(set_output) == "out/images/icons"


def test_missing_parent(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    """Without 'parents' only the last part of the path is created, like 'mkdir' without '-p'"""
    set_inputs(monkeypatch, directory="out/images/icons")
    failed = mocker.spy(mkdir_main, "set_failed")
    with pytest.raises(SystemExit):
        main()
    assert failed.call_args.args[0] == ("Cannot create 'out/images/icons': 'out/images' doesn't exist, "
                                        "set 'parents' to create the parent directories")
    assert not (project / "out" / "images").exists()


def test_missing_parent_outside_working_directory(project: Path, monkeypatch: pytest.MonkeyPatch,
                                                  mocker: MockerFixture) -> None:
    """An allowed path outside the working directory is named in full, it has no relative form"""
    outside = (project.parent / "outside").as_posix()
    set_inputs(monkeypatch, directory=f"{outside}/images", allow_outside_working_directory=True)
    failed = mocker.spy(mkdir_main, "set_failed")
    with pytest.raises(SystemExit):
        main()
    assert failed.call_args.args[0] == (f"Cannot create '{outside}/images': '{outside}' doesn't exist, "
                                        f"set 'parents' to create the parent directories")


def test_existing_directory(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    """An existing directory is not an error: the task can run again without failing"""
    set_inputs(monkeypatch, directory="out")
    set_output = mocker.patch("prepare_mkdir.main.set_output")
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_not_called()
    assert (project / "out").is_dir()
    assert created(set_output) == "out"


def test_existing_file(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    set_inputs(monkeypatch, directory="test.txt")
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_called_once()
    assert (project / "test.txt").read_text() == "test.txt"


def test_absolute_path(project: Path, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
    """An absolute path inside the working directory is output relative to it, like the other tasks"""
    set_inputs(monkeypatch, directory=str(project / "out" / "images"))
    set_output = mocker.patch("prepare_mkdir.main.set_output")
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_not_called()
    assert (project / "out" / "images").is_dir()
    assert created(set_output) == "out/images"


@pytest.mark.parametrize("directory", ["..", "../outside", "out/../../outside", "ABSOLUTE"])
def test_outside_working_directory_fails(directory: str, project: Path, monkeypatch: pytest.MonkeyPatch,
                                         mocker: MockerFixture) -> None:
    """The task used to create any directory, also next to or outside the project"""
    if directory == "ABSOLUTE":
        directory = (project.parent / "outside").as_posix()
    set_inputs(monkeypatch, directory=directory, parents=True)
    failed = mocker.spy(mkdir_main, "set_failed")
    with pytest.raises(SystemExit):
        main()
    assert failed.call_args.args[0] == (f"The directory '{directory}' is outside the working directory, set "
                                        f"'allow-outside-working-directory' to allow this")
    assert not (project.parent / "outside").exists()


def test_outside_working_directory_allowed(project: Path, monkeypatch: pytest.MonkeyPatch,
                                           mocker: MockerFixture) -> None:
    set_inputs(monkeypatch, directory="../outside", allow_outside_working_directory=True)
    set_output = mocker.patch("prepare_mkdir.main.set_output")
    failed = mocker.patch("prepare_mkdir.main.set_failed")
    main()
    failed.assert_not_called()
    assert (project.parent / "outside").is_dir()
    # A directory outside the working directory has no relative form
    assert created(set_output) == (project.parent / "outside").as_posix()
