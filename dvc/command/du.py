import argparse
import json
import logging
import os
from collections import Counter
from functools import reduce

from dvc.command import completion
from dvc.command.base import append_doc_link
from dvc.command.ls import CmdList
from dvc.command.ls.output_formatter import convert_bytes
from dvc.exceptions import DvcException
from dvc.ui import ui

logger = logging.getLogger(__name__)


class CmdDiskUsage(CmdList):
    def _calculate_total_per_directory(self, entries):
        directory_sizes = Counter()
        updated_entries = []
        for e in entries:
            parts = os.path.normpath(e["path"]).split(os.sep)

            # Let root level entries that are not directories as is
            if len(parts) == 1 and not e["isdir"]:
                updated_entries.append(e)
                continue

            directory_sizes[parts[0]] += e["size"]

        # Combine calculated directory entries and the root level file entries
        for directory_item in directory_sizes.items():
            updated_entries.append(
                {
                    "path": directory_item[0],
                    "size": directory_item[1],
                    "isdir": True,
                    "isexec": False,
                    "isout": False,
                }
            )

        return sorted(updated_entries, key=lambda entry: entry["path"])

    def run(self):
        from dvc.repo import Repo

        try:
            entries = Repo.ls(
                self.args.url,
                self.args.path,
                rev=self.args.rev,
                recursive=True,
                with_size=True,
                dvc_only=self.args.dvc_only,
            )

            if not self.args.recursive:
                entries = self._calculate_total_per_directory(entries)

            if self.args.summarize:
                sizes = [a["size"] for a in entries]
                total_size = reduce(
                    lambda a, b: a + b,
                    sizes,
                    0,
                )

                if self.args.human_readable:
                    total_size = convert_bytes(total_size)

                if self.args.show_json:
                    ui.write(json.dumps({"total": total_size}))
                else:
                    ui.write(total_size)

            elif self.args.show_json:
                if self.args.human_readable:
                    for entry in entries:
                        entry["size"] = convert_bytes(entry["size"])

                ui.write(json.dumps(entries))
            elif entries:
                entries = self.prettify_entries(
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
        "-s",
        "--summarize",
        action="store_true",
        help="Display only a total disk usage.",
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
