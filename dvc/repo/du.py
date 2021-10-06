from dvc.path_info import PathInfo


def du(url, path=None, rev=None, total=False):
    """Methods for getting (estimated) disk usage of directories and files.

    Args:
        url (str): the repo url
        path (str, optional): relative path into the repo
        rev (str, optional): SHA commit, branch or tag name

    Returns:
        list of `entry`

    Notes:
        `entry` is a tuple with structure ("path": size)
    """
    from . import Repo

    with Repo.open(url, rev=rev, subrepos=True, uninitialized=True) as repo:
        path_info = PathInfo(repo.root_dir)
        if path:
            path_info /= path

        disk_usage = repo.repo_fs.du(path_info, total=total)

        # NOTE: I know adding a " ." and then stripping the whitespace
        #   with [1:] is a little hackish, but it works and makes the
        #   output same as the unix du command

        # normalize directory names
        disk_usage = [
            (
                entry[0].fspath.replace(repo.root_dir, "" if path else " .")[
                    1:
                ],
                entry[1],
            )
            for entry in disk_usage
        ]

        return disk_usage
