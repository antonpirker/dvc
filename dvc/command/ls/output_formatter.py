import os


def convert_bytes(num):
    """
    Convert bytes to kilobytes, megabytes, gigabytes, ...
    """
    step_unit = 1024.0

    for unit in ["", "K", "M", "G", "T", "P"]:
        if num < step_unit:
            return f"{num:.0f}{unit}"
        num /= step_unit

    return f"{num*step_unit:.0f}{unit}"


class OutputFormatter:
    default_colors = "rs=0:di=01;34:ex=01;32"

    def __init__(
        self,
        default_colors=None,
        with_color=False,
        with_size=False,
        human_readable=False,
    ):
        self.with_color = with_color
        self.with_size = with_size
        self.human_readable = human_readable
        self._color_for_file_extension = {}
        self._color_for_code = {}
        self._load_colors(
            default_colors
            or os.environ.get("LS_COLORS")
            or OutputFormatter.default_colors
        )

    def _load_colors(self, default_colors):
        for item in default_colors.split(":"):
            try:
                code, color = item.split("=", 1)
            except ValueError:
                continue
            if code.startswith("*."):
                self._color_for_file_extension[code[1:]] = color
            else:
                self._color_for_code[code] = color

    def format(self, entry):
        text = entry["path"]
        output = ""

        if self.with_color:
            if entry.get("isout", False) and "out" in self._color_for_code:
                output = self._format(text, code="out")

            elif entry.get("isdir", False):
                output = self._format(text, code="di")

            elif entry.get("isexec", False):
                output = self._format(text, code="ex")

            else:
                _, ext = os.path.splitext(text)
                output = self._format(text, ext=ext)
        else:
            output = text

        if self.with_size:
            size = entry.get(
                "size", 0
            )  # TODO: remove default when the size always in entry
            if self.human_readable:
                size_string = convert_bytes(size)
                output = f"{size_string:<8s}\t{output}"
            else:
                output = f"{size:<8d}\t{output}"

        return output

    def _format(self, text, code=None, ext=None):
        val = None
        if ext:
            val = self._color_for_file_extension.get(ext, None)
        if code:
            val = self._color_for_code.get(code, None)

        if not val:
            return text
        rs = self._color_for_code.get("rs", 0)
        return f"\033[{val}m{text}\033[{rs}m"
