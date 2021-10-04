import argparse
import logging

from dvc.command import completion
from dvc.command.base import CmdBaseNoRepo, append_doc_link
from dvc.exceptions import DvcException
from dvc.ui import ui

logger = logging.getLogger(__name__)


class CmdDiskUsage(CmdBaseNoRepo):
    def run(self):
        from dvc.repo import Repo

        try:
            entries = Repo.du(
                self.args.url,
                self.args.path,
                rev=self.args.rev,
                recursive=self.args.recursive,
                dvc_only=self.args.dvc_only,
            )

            if entries:
                ui.write(
                    "\n".join([f"{entry[1]}\t{entry[0]}" for entry in entries])
                )

            return 0
        except DvcException:
            logger.exception(f"failed to list '{self.args.url}'")
            return 1


def add_parser(subparsers, parent_parser):
    DISK_USAGE_HELP = (
        "List disk usage of repository contents, including files"
        " and directories tracked by DVC and by Git."
    )
    disk_usage_parser = subparsers.add_parser(
        "du",
        parents=[parent_parser],
        description=append_doc_link(DISK_USAGE_HELP, "du"),
        help=DISK_USAGE_HELP,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    disk_usage_parser.add_argument(
        "url", help="Location of DVC repository to list disk usage"
    )
    disk_usage_parser.add_argument(
        "-R",
        "--recursive",
        action="store_true",
        help="Recursively list files.",
    )
    disk_usage_parser.add_argument(
        "-H",
        "--human-readable",
        action="store_true",
        help="Output disk sizes in humand readable form (like MB, GB, ..).",
    )
    disk_usage_parser.add_argument(
        "--dvc-only", action="store_true", help="Show only DVC outputs."
    )
    disk_usage_parser.add_argument(
        "--rev",
        nargs="?",
        help="Git revision (e.g. SHA, branch, tag)",
        metavar="<commit>",
    )
    disk_usage_parser.add_argument(
        "path",
        nargs="?",
        help="Path to directory within the repository to list disk usage for",
    ).complete = completion.DIR
    disk_usage_parser.set_defaults(func=CmdDiskUsage)
