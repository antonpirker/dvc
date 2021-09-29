import json

from dvc.cli import parse_args
from dvc.command.du import CmdDiskUsage


def _test_cli(mocker, *args):
    cli_args = parse_args(["du", *args])
    assert cli_args.func == CmdDiskUsage

    cmd = cli_args.func(cli_args)
    m = mocker.patch("dvc.repo.Repo.ls")

    assert cmd.run() == 0
    return m


def test_du(mocker):
    url = "local_dir"
    m = _test_cli(mocker, url)
    m.assert_called_once_with(
        url, None, recursive=False, rev=None, with_size=True, dvc_only=False
    )


def test_du_recursive(mocker):
    url = "local_dir"
    m = _test_cli(mocker, url, "-R")
    m.assert_called_once_with(
        url, None, recursive=True, rev=None, with_size=True, dvc_only=False
    )


def test_du_summarize(mocker):
    url = "local_dir"
    m = _test_cli(mocker, url, "-s")
    m.assert_called_once_with(
        url, None, recursive=True, rev=None, with_size=True, dvc_only=False
    )


def test_du_summarize_and_recursive(mocker):
    url = "local_dir"
    m = _test_cli(mocker, url, "-sR")
    m.assert_called_once_with(
        url, None, recursive=True, rev=None, with_size=True, dvc_only=False
    )


def test_du_human_readable(mocker):
    url = "local_dir"
    m = _test_cli(mocker, url, "-H")
    m.assert_called_once_with(
        url, None, recursive=False, rev=None, with_size=True, dvc_only=False
    )


def test_du_sumarize_human_readable(mocker):
    url = "local_dir"
    m = _test_cli(mocker, url, "-sH")
    m.assert_called_once_with(
        url, None, recursive=True, rev=None, with_size=True, dvc_only=False
    )


def test_du_git_ssh_rev(mocker):
    url = "git@github.com:repo"
    m = _test_cli(mocker, url, "--rev", "123")
    m.assert_called_once_with(
        url, None, recursive=False, rev="123", with_size=True, dvc_only=False
    )


def test_du_targets(mocker):
    url = "local_dir"
    target = "subdir"
    m = _test_cli(mocker, url, target)
    m.assert_called_once_with(
        url, target, recursive=False, rev=None, with_size=True, dvc_only=False
    )


def test_du_outputs_only(mocker):
    url = "local_dir"
    m = _test_cli(mocker, url, None, "--dvc-only")
    m.assert_called_once_with(
        url, None, recursive=False, rev=None, with_size=True, dvc_only=True
    )


def test_du_show_json(mocker, capsys):
    cli_args = parse_args(["du", "local_dir", "--show-json"])
    assert cli_args.func == CmdDiskUsage

    cmd = cli_args.func(cli_args)

    result = [{"key": "val"}]
    mocker.patch("dvc.repo.Repo.ls", return_value=result)

    assert cmd.run() == 0
    out, _ = capsys.readouterr()
    assert json.dumps(result) in out
