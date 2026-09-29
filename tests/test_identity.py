"""The package and CLI name the maker as Saffron and make no unsourced claims."""
import sqg
from sqg import cli


def test_package_identity():
    assert sqg.__author__ == "Saffron"
    assert sqg.__license__ == "Proprietary, Saffron"
    assert sqg.__version__ == "1.0.0"


def test_version_command_output(capsys):
    assert cli.cmd_version(None) == 0
    out = capsys.readouterr().out.splitlines()
    assert out == [
        "SQG v1.0.0",
        "Saffron Quality Gate: an executable quality gate for code, content and configuration.",
        "© Saffron · saffronsystems.io",
    ]
    text = "\n".join(out)
    assert "Group" not in text and "world's first" not in text
