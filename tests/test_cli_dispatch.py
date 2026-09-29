"""main() routes each subcommand to its handler and exits with that handler's code."""
import sys
import pytest
from sqg import cli

CASES = {"scan": "cmd_scan", "audit": "cmd_audit", "gate": "cmd_gate", "check": "cmd_check", "version": "cmd_version"}


@pytest.mark.parametrize("command,handler", sorted(CASES.items()))
def test_each_subcommand_exits_with_its_handler_code(monkeypatch, command, handler):
    codes = {name: 10 + i for i, name in enumerate(sorted(CASES.values()))}
    for name, code in codes.items():
        monkeypatch.setattr(cli, name, lambda args, c=code: c)
    monkeypatch.setattr(sys, "argv", ["sqg", command])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == codes[handler]


def test_version_flag_prints_help_and_returns_zero(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["sqg", "--version"])
    assert cli.main() == 0
    assert "usage: sqg" in capsys.readouterr().out


def test_no_command_prints_help_and_returns_zero(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["sqg"])
    assert cli.main() == 0
    out = capsys.readouterr().out
    assert "usage: sqg" in out and "executable quality enforcement" in out


def test_logo_makes_no_unsourced_claim():
    assert "world's first" not in cli.LOGO and "SAFFRON QUALITY GATE" in cli.LOGO
