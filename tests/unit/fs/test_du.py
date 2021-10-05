import pytest

from dvc.fs.repo import RepoFileSystem
from dvc.path_info import PathInfo


def _print_dir(path):
    import os
    import sys

    for root, dirs, files in os.walk(str(path)):
        sys.stderr.write(f"\n{root}")
        for d in dirs:
            sys.stderr.write(f"\n- {d}")
        for d in files:
            sys.stderr.write(f"\n~ {d}")

    sys.stderr.writelines(["\n", "\n"])


NAME = 0
SIZE = 1
RESULT_IDX = 2
EXPECTED_RESULTS = {
    # {total}-{maxdepth}-{subdir}
    "False-None-": ("data", 39, 3),
    "False-None-data": ("data", 39, 0),
    "False-None-data/data-b.json": ("data/data-b.json", 22),
}


@pytest.mark.parametrize("subdir", ["", "data", "data/data-b.json"])
@pytest.mark.parametrize("maxdepth", [None])
@pytest.mark.parametrize("total", [False])
def test_du(tmp_dir, dvc, total, maxdepth, subdir):
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

    fs = RepoFileSystem(repo=dvc)
    root = PathInfo(tmp_dir)
    du_result = fs.du(root / subdir, total=total, maxdepth=maxdepth)

    import sys

    sys.stderr.write(str(du_result))

    expected = EXPECTED_RESULTS[f"{total}-{maxdepth}-{subdir}"]
    result = du_result[expected[RESULT_IDX]]

    assert str(result[NAME]) == expected[NAME]
    assert result[SIZE] == expected[SIZE]
