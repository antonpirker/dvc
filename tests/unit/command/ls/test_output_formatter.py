from dvc.command.ls.output_formatter import OutputFormatter


def colorize(output_formatter):
    def _colorize(f, spec=""):
        fs_path = {
            "path": f,
            "isexec": "e" in spec,
            "isdir": "d" in spec,
            "isout": "o" in spec,
        }
        print(fs_path)
        return output_formatter.format(fs_path)

    return _colorize


def test_output_formatter_color_out_file():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors, with_color=True
    )
    assert colorize(output_formatter)("file", "o") == "file"


def test_output_formatter_color_out_dir():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors, with_color=True
    )
    assert colorize(output_formatter)("dir", "do") == "\x1b[01;34mdir\x1b[0m"


def test_output_formatter_color_out_exec():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors, with_color=True
    )
    assert (
        colorize(output_formatter)("script.sh", "eo")
        == "\x1b[01;32mscript.sh\x1b[0m"
    )


def test_output_formatter_color_out_ext():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors + ":*.xml=01;33", with_color=True
    )
    assert (
        colorize(output_formatter)("file.xml", "o")
        == "\x1b[01;33mfile.xml\x1b[0m"
    )


def test_output_formatter_color_file():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors, with_color=True
    )
    assert colorize(output_formatter)("file") == "file"


def test_output_formatter_color_dir():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors, with_color=True
    )
    assert colorize(output_formatter)("dir", "d") == "\x1b[01;34mdir\x1b[0m"


def test_output_formatter_color_exec():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors, with_color=True
    )
    assert (
        colorize(output_formatter)("script.sh", "e")
        == "\x1b[01;32mscript.sh\x1b[0m"
    )


def test_output_formatter_color_ext():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors + ":*.xml=01;33", with_color=True
    )
    assert (
        colorize(output_formatter)("file.xml") == "\x1b[01;33mfile.xml\x1b[0m"
    )


def test_ls_repo_with_custom_color_env_defined(monkeypatch):
    monkeypatch.setenv("LS_COLORS", "rs=0:di=01;34:*.xml=01;31:*.dvc=01;33:")
    output_formatter = OutputFormatter(with_color=True)
    colorizer = colorize(output_formatter)

    assert colorizer(".dvcignore") == ".dvcignore"
    assert colorizer(".gitignore") == ".gitignore"
    assert colorizer("README.md") == "README.md"
    assert colorizer("data", "d") == "\x1b[01;34mdata\x1b[0m"
    assert colorizer("structure.xml") == "\x1b[01;31mstructure.xml\x1b[0m"
    assert (
        colorizer("structure.xml.dvc") == "\x1b[01;33mstructure.xml.dvc\x1b[0m"
    )
