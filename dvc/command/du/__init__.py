import argparse
import logging

from dvc.command import completion
from dvc.command.base import CmdBaseNoRepo, append_doc_link
from dvc.command.ls.output_formatter import OutputFormatter
from dvc.exceptions import DvcException
from dvc.ui import ui

logger = logging.getLogger(__name__)


def _prettify(
    entries, with_color=False, with_size=False, human_readable=False
):
    output_formatter = OutputFormatter(
        with_color=with_color,
        with_size=with_size,
        human_readable=human_readable,
    )
    return [output_formatter.format(entry) for entry in entries]


class CmdDiskUsage(CmdBaseNoRepo):
    def run(self):
        from dvc.repo import Repo

        try:
            entries = Repo.ls(
                self.args.url,
                self.args.path,
                rev=self.args.rev,
                recursive=self.args.recursive,
                with_size=True,
                dvc_only=self.args.dvc_only,
            )
            if self.args.show_json:
                import json

                ui.write(json.dumps(entries))
            elif entries:
                entries = _prettify(
                    entries,
                    with_color=True,
                    with_size=True,
                    human_readable=self.args.human_readable,
                )
                ui.write("\n".join(entries))
            return 0
        except DvcException:
            logger.exception(f"failed to list '{self.args.url}'")
            return 1


def add_parser(subparsers, parent_parser):
    DISK_USAGE_HELP = "List repository contents with disk usage."
    list_parser = subparsers.add_parser(
        "du",
        parents=[parent_parser],
        description=append_doc_link(DISK_USAGE_HELP, "du"),
        help=DISK_USAGE_HELP,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    list_parser.add_argument(
        "url", help="Location of DVC repository to list disk usage of"
    )
    list_parser.add_argument(
        "-R",
        "--recursive",
        action="store_true",
        help="Recursively list files.",
    )
    list_parser.add_argument(
        "-H",
        "--human-readable",
        action="store_true",
        help="Show disk usage in human readable form.",
    )
    list_parser.add_argument(
        "--dvc-only", action="store_true", help="Show only DVC outputs."
    )
    list_parser.add_argument(
        "--show-json", action="store_true", help="Show output in JSON format."
    )
    list_parser.add_argument(
        "--rev",
        nargs="?",
        help="Git revision (e.g. SHA, branch, tag)",
        metavar="<commit>",
    )
    list_parser.add_argument(
        "path",
        nargs="?",
        help="Path to directory within the repository to list outputs for",
    ).complete = completion.DIR
    list_parser.set_defaults(func=CmdDiskUsage)
