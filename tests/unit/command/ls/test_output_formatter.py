from dvc.command.ls.output_formatter import OutputFormatter, convert_bytes


def format(output_formatter):
    def _format(f, spec=""):
        fs_path = {
            "path": f,
            "isexec": "e" in spec,
            "isdir": "d" in spec,
            "isout": "o" in spec,
        }

        if output_formatter.with_size:
            fs_path["size"] = 123456

        return output_formatter.format(fs_path)

    return _format


def test_output_formatter_color_out_file():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors, with_color=True
    )
    assert format(output_formatter)("file", "o") == "file"


def test_output_formatter_color_out_dir():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors, with_color=True
    )
    assert format(output_formatter)("dir", "do") == "\x1b[01;34mdir\x1b[0m"


def test_output_formatter_color_out_exec():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors, with_color=True
    )
    assert (
        format(output_formatter)("script.sh", "eo")
        == "\x1b[01;32mscript.sh\x1b[0m"
    )


def test_output_formatter_color_out_ext():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors + ":*.xml=01;33", with_color=True
    )
    assert (
        format(output_formatter)("file.xml", "o")
        == "\x1b[01;33mfile.xml\x1b[0m"
    )


def test_output_formatter_color_file():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors, with_color=True
    )
    assert format(output_formatter)("file") == "file"


def test_output_formatter_color_dir():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors, with_color=True
    )
    assert format(output_formatter)("dir", "d") == "\x1b[01;34mdir\x1b[0m"


def test_output_formatter_color_exec():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors, with_color=True
    )
    assert (
        format(output_formatter)("script.sh", "e")
        == "\x1b[01;32mscript.sh\x1b[0m"
    )


def test_output_formatter_color_ext():
    output_formatter = OutputFormatter(
        OutputFormatter.default_colors + ":*.xml=01;33", with_color=True
    )
    assert format(output_formatter)("file.xml") == "\x1b[01;33mfile.xml\x1b[0m"


def test_output_formatter_no_color():
    output_formatter = OutputFormatter()
    assert format(output_formatter)("file", "o") == "file"
    assert format(output_formatter)("dir", "do") == "dir"
    assert format(output_formatter)("script.sh", "eo") == "script.sh"
    assert format(output_formatter)("file.xml", "o") == "file.xml"
    assert format(output_formatter)("file") == "file"
    assert format(output_formatter)("dir", "d") == "dir"
    assert format(output_formatter)("script.sh", "e") == "script.sh"
    assert format(output_formatter)("file.xml") == "file.xml"


def test_output_formatter_with_size():
    output_formatter = OutputFormatter(with_size=True)
    assert format(output_formatter)("file", "o") == "123456  \tfile"
    assert format(output_formatter)("dir", "do") == "123456  \tdir"
    assert format(output_formatter)("script.sh", "eo") == "123456  \tscript.sh"
    assert format(output_formatter)("file.xml", "o") == "123456  \tfile.xml"
    assert format(output_formatter)("file") == "123456  \tfile"
    assert format(output_formatter)("dir", "d") == "123456  \tdir"
    assert format(output_formatter)("script.sh", "e") == "123456  \tscript.sh"
    assert format(output_formatter)("file.xml") == "123456  \tfile.xml"


def test_output_formatter_with_size_human_readable():
    output_formatter = OutputFormatter(with_size=True, human_readable=True)
    assert format(output_formatter)("file", "o") == "121K    \tfile"
    assert format(output_formatter)("dir", "do") == "121K    \tdir"
    assert format(output_formatter)("script.sh", "eo") == "121K    \tscript.sh"
    assert format(output_formatter)("file.xml", "o") == "121K    \tfile.xml"
    assert format(output_formatter)("file2") == "121K    \tfile2"
    assert format(output_formatter)("dir2", "d") == "121K    \tdir2"
    assert (
        format(output_formatter)("script2.sh", "e") == "121K    \tscript2.sh"
    )
    assert format(output_formatter)("file2.xml") == "121K    \tfile2.xml"


def test_ls_repo_with_custom_color_env_defined(monkeypatch):
    monkeypatch.setenv("LS_COLORS", "rs=0:di=01;34:*.xml=01;31:*.dvc=01;33:")
    output_formatter = OutputFormatter(with_color=True)
    colorizer = format(output_formatter)

    assert colorizer(".dvcignore") == ".dvcignore"
    assert colorizer(".gitignore") == ".gitignore"
    assert colorizer("README.md") == "README.md"
    assert colorizer("data", "d") == "\x1b[01;34mdata\x1b[0m"
    assert colorizer("structure.xml") == "\x1b[01;31mstructure.xml\x1b[0m"
    assert (
        colorizer("structure.xml.dvc") == "\x1b[01;33mstructure.xml.dvc\x1b[0m"
    )


def test_convert_bytes():
    tests = [
        (123, "123"),
        (1023, "1023"),
        (1024, "1K"),
        (32345678, "31M"),
        (12312344320, "11G"),
        (5724696466209, "5T"),
        (123443546457768445, "110P"),
        (1152922000000000000, "1024P"),
    ]

    for test in tests:
        assert convert_bytes(test[0]) == test[1]
