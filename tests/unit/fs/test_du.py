import os
import sys

import pytest

from dvc.fs.dvc import DvcFileSystem
from dvc.fs.local import LocalFileSystem
from dvc.path_info import PathInfo


def _print_dir(path):
    for root, dirs, files in os.walk(str(path)):
        sys.stderr.write(f"\n{root}")
        for d in dirs:
            sys.stderr.write(f"\n- {d}")
        for d in files:
            sys.stderr.write(f"\n~ {d}")

    sys.stderr.writelines(["\n", "\n"])


NAME = 0
SIZE = 1


def _run_test(tmp_dir, fs, subdir, total, maxdepth, expected_results):
    root = PathInfo(tmp_dir)
    du_result = fs.du(root / subdir, total=total, maxdepth=maxdepth)
    sys.stderr.write(str(du_result))

    expected = expected_results[f"{total}-{maxdepth}-{subdir}"]
    result = du_result[expected["result_index"]]

    assert str(result[NAME]) == expected["name"]
    assert result[SIZE] == expected["size"]

    if total:
        assert len(du_result) == 1


# Key is: {total}-{maxdepth}-{subdir}
EXPECTED_RESULTS_LOCAL = {
    "False-None-": {
        "name": ".",
        "size": 145977,
        "result_index": -1,
    },
    "False-None-experiments": {
        "name": "experiments",
        "size": 34,
        "result_index": -1,
    },
    "False-None-data/data-b.json": {
        "name": "data/data-b.json",
        "size": 22,
        "result_index": 0,
    },
    "True-None-": {
        "name": ".",
        "size": 145977,
        "result_index": 0,
    },
    "True-None-experiments": {
        "name": "experiments",
        "size": 34,
        "result_index": 0,
    },
    "True-None-data/data-b.json": {
        "name": "data/data-b.json",
        "size": 22,
        "result_index": 0,
    },
}


@pytest.mark.parametrize("subdir", ["", "experiments", "data/data-b.json"])
@pytest.mark.parametrize("maxdepth", [None])
@pytest.mark.parametrize("total", [False, True])
def test_local_fs_du(tmp_dir, dvc, total, maxdepth, subdir):
    tmp_dir.gen(
        {  # 73 bytes
            "data": {  # 39 bytes
                "data-a.json": '{"some": "data"}\n',  # 17 bytes
                "data-b.json": '{"some_more": "data"}\n',  # 22 bytes
            },
            "experiments": {  # 34 bytes
                "experiment-a": {  # 34 bytes
                    "datafile-1.csv": "one;two;three\n",  # 14 bytes
                    "datafile-2.csv": "four;five;six;seven\n",  # 20 bytes
                },
                "experiment-b": {},  # 0 bytes
            },
        }
    )
    _print_dir(tmp_dir)

    fs = LocalFileSystem(repo=dvc)
    _run_test(tmp_dir, fs, subdir, total, maxdepth, EXPECTED_RESULTS_LOCAL)


# Key is: {total}-{maxdepth}-{subdir}
EXPECTED_RESULTS_DVC = {
    "False-None-": {
        "name": ".",
        "size": 56,
        "result_index": -1,
    },
    "False-None-experiments": {
        "name": "experiments",
        "size": 34,
        "result_index": -1,
    },
    "False-None-data/data-b.json": {
        "name": "data/data-b.json",
        "size": 22,
        "result_index": 0,
    },
    "True-None-": {
        "name": ".",
        "size": 56,
        "result_index": 0,
    },
    "True-None-experiments": {
        "name": "experiments",
        "size": 34,
        "result_index": 0,
    },
    "True-None-data/data-b.json": {
        "name": "data/data-b.json",
        "size": 22,
        "result_index": 0,
    },
}


@pytest.mark.parametrize("subdir", ["", "experiments", "data/data-b.json"])
@pytest.mark.parametrize("maxdepth", [None])
@pytest.mark.parametrize("total", [False, True])
def test_dvc_fs_du(tmp_dir, dvc, total, maxdepth, subdir):
    tmp_dir.gen(
        {  # 56 bytes
            "data": {  # 22 bytes
                "data-a.json": '{"some": "data"}\n',  # 0 bytes (not in dvc)
                "data-b.json": '{"some_more": "data"}\n',  # 22 bytes
            },
            "experiments": {  # 34 bytes
                "experiment-a": {  # 34 bytes
                    "datafile-1.csv": "one;two;three\n",  # 14 bytes
                    "datafile-2.csv": "four;five;six;seven\n",  # 20 bytes
                },
                "experiment-b": {},  # 0 bytes
            },
        }
    )
    dvc.add("data/data-b.json")
    dvc.add("experiments/experiment-a")

    _print_dir(tmp_dir)

    fs = DvcFileSystem(repo=dvc)
    _run_test(tmp_dir, fs, subdir, total, maxdepth, EXPECTED_RESULTS_DVC)


# Key is: {total}-{maxdepth}-{subdir}
EXPECTED_RESULTS_GIT = {
    "False-None-": {
        "name": ".",
        "size": 14906,
        "result_index": -1,
    },
    "False-None-experiments": {
        "name": "experiments",
        "size": 34,
        "result_index": -1,
    },
    "False-None-data/data-b.json": {
        "name": "data/data-b.json",
        "size": 22,
        "result_index": 0,
    },
    "True-None-": {
        "name": ".",
        "size": 14906,
        "result_index": 0,
    },
    "True-None-experiments": {
        "name": "experiments",
        "size": 34,
        "result_index": 0,
    },
    "True-None-data/data-b.json": {
        "name": "data/data-b.json",
        "size": 22,
        "result_index": 0,
    },
}


@pytest.mark.parametrize("subdir", ["", "experiments", "data/data-b.json"])
@pytest.mark.parametrize("maxdepth", [None])
@pytest.mark.parametrize("total", [False, True])
def test_git_fs_du(tmp_dir, scm, dvc, total, maxdepth, subdir):
    tmp_dir.scm_gen(
        {  # 56 bytes
            "data": {  # 22 bytes
                "data-a.json": '{"some": "data"}\n',  # 0 bytes (not in dvc)
                "data-b.json": '{"some_more": "data"}\n',  # 22 bytes
            },
            "experiments": {  # 34 bytes
                "experiment-a": {  # 34 bytes
                    "datafile-1.csv": "one;two;three\n",  # 14 bytes
                    "datafile-2.csv": "four;five;six;seven\n",  # 20 bytes
                },
                "experiment-b": {},  # 0 bytes
            },
        },
        commit="added data files",
    )

    _print_dir(tmp_dir)

    fs = scm.get_fs("master")
    _run_test(tmp_dir, fs, subdir, total, maxdepth, EXPECTED_RESULTS_GIT)
