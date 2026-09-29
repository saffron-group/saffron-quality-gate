"""Every CLI command builds the right tool invocation and reports the tool's real outcome."""
import subprocess
import sys
from types import SimpleNamespace

import pytest
from sqg import cli


class Recorder:
    """Stands in for subprocess.run: records each call and returns a scripted result."""

    def __init__(self, returncode=0, stdout="", stderr="", raises=None):
        self.calls = []
        self.result = SimpleNamespace(returncode=returncode, stdout=stdout, stderr=stderr)
        self.raises = raises

    def __call__(self, argv, **kwargs):
        self.calls.append((argv, kwargs))
        if self.raises:
            raise self.raises
        return self.result


def test_cmd_exists_asks_which_and_reads_the_exit_code(monkeypatch):
    found = Recorder(returncode=0)
    monkeypatch.setattr(cli.subprocess, "run", found)
    assert cli.cmd_exists("ruff") is True
    assert found.calls == [(["which", "ruff"], {"capture_output": True})]
    monkeypatch.setattr(cli.subprocess, "run", Recorder(returncode=1))
    assert cli.cmd_exists("ruff") is False


def test_run_tool_reports_a_missing_tool_without_running_anything(monkeypatch, tmp_path):
    rec = Recorder()
    monkeypatch.setattr(cli.subprocess, "run", rec)
    missing = str(tmp_path / "nope.py")
    assert cli.run_tool(missing, ["--x"]) == (-1, "", f"tool not found: {missing}")
    assert rec.calls == []


def test_run_tool_runs_the_script_with_this_python_and_returns_its_outcome(monkeypatch, tmp_path):
    tool = tmp_path / "tool.py"
    tool.write_text("")
    rec = Recorder(returncode=3, stdout="out", stderr="err")
    monkeypatch.setattr(cli.subprocess, "run", rec)
    assert cli.run_tool(str(tool), ["--a", "b"], timeout=7) == (3, "out", "err")
    assert rec.calls == [([sys.executable, str(tool), "--a", "b"],
                          {"capture_output": True, "text": True, "timeout": 7})]
    rec2 = Recorder()
    monkeypatch.setattr(cli.subprocess, "run", rec2)
    cli.run_tool(str(tool), [])
    assert rec2.calls[0][1]["timeout"] == 120


@pytest.mark.parametrize("exc,message", [
    (subprocess.TimeoutExpired(cmd="x", timeout=1), "timeout"),
    (FileNotFoundError(), "python not found"),
])
def test_run_tool_turns_failures_into_an_error_result(monkeypatch, tmp_path, exc, message):
    tool = tmp_path / "tool.py"
    tool.write_text("")
    monkeypatch.setattr(cli.subprocess, "run", Recorder(raises=exc))
    assert cli.run_tool(str(tool), []) == (-1, "", message)


@pytest.mark.parametrize("command,script_attr", [("cmd_scan", "SCANNER"), ("cmd_audit", "SCORER")])
@pytest.mark.parametrize("strict", [False, True])
def test_scan_and_audit_pass_path_format_and_strict(monkeypatch, capsys, command, script_attr, strict):
    seen = []

    def fake_run_tool(path, args):
        seen.append((path, args))
        return 5, "report", "problem"

    monkeypatch.setattr(cli, "run_tool", fake_run_tool)
    args = SimpleNamespace(path="src", format="json", strict=strict)
    assert getattr(cli, command)(args) == 5
    expected = ["--path", "src", "--format", "json"] + (["--strict"] if strict else [])
    assert seen == [(getattr(cli, script_attr), expected)]
    assert capsys.readouterr().out == "report\n"


@pytest.mark.parametrize("command", ["cmd_scan", "cmd_audit"])
def test_scan_and_audit_print_the_error_when_there_is_no_output(monkeypatch, capsys, command):
    monkeypatch.setattr(cli, "run_tool", lambda path, args: (-1, "", "tool not found: x"))
    assert getattr(cli, command)(SimpleNamespace(path=".", format="table", strict=False)) == -1
    assert capsys.readouterr().out == "tool not found: x\n"


def test_gate_refuses_cleanly_when_the_runner_is_missing(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(cli, "GATE", str(tmp_path / "missing.sh"))
    rec = Recorder()
    monkeypatch.setattr(cli.subprocess, "run", rec)
    assert cli.cmd_gate(SimpleNamespace(path=".", strict=False)) == 1
    assert "Gate runner not found" in capsys.readouterr().out
    assert rec.calls == []


@pytest.mark.parametrize("strict,flags", [(False, ""), (True, " --strict")])
def test_gate_runs_the_runner_and_returns_its_code(monkeypatch, capsys, tmp_path, strict, flags):
    gate = tmp_path / "gate.sh"
    gate.write_text("")
    monkeypatch.setattr(cli, "GATE", str(gate))
    rec = Recorder(returncode=4, stdout="gate says hi")
    monkeypatch.setattr(cli.subprocess, "run", rec)
    assert cli.cmd_gate(SimpleNamespace(path="app", strict=strict)) == 4
    assert rec.calls == [(["bash", str(gate), "app", flags], {"text": True, "timeout": 180})]
    assert capsys.readouterr().out == "gate says hi\n"


def test_gate_prints_an_empty_line_when_the_runner_is_silent(monkeypatch, capsys, tmp_path):
    gate = tmp_path / "gate.sh"
    gate.write_text("")
    monkeypatch.setattr(cli, "GATE", str(gate))
    monkeypatch.setattr(cli.subprocess, "run", Recorder(returncode=0, stdout=None))
    assert cli.cmd_gate(SimpleNamespace(path=".", strict=False)) == 0
    assert capsys.readouterr().out == "\n"


def test_check_reports_each_tool_and_script_honestly(monkeypatch, capsys, tmp_path):
    installed = {"ruff", "pytest"}
    monkeypatch.setattr(cli, "cmd_exists", lambda name: name in installed)
    present = tmp_path / "scanner.py"
    present.write_text("")
    monkeypatch.setattr(cli, "SCANNER", str(present))
    monkeypatch.setattr(cli, "SCORER", str(tmp_path / "no-scorer.py"))
    monkeypatch.setattr(cli, "GATE", str(tmp_path / "no-gate.sh"))
    assert cli.cmd_check(None) == 0
    out = capsys.readouterr().out
    lines = out.splitlines()
    assert "SQG v1.0.0" in out and "Environment Check" in out
    assert f"{'ruff':<15} {'✅':>8}  {'Code linting (Correctness)':<40}" in lines
    assert f"{'mypy':<15} {'❌':>8}  {'Type checking (Correctness)':<40}" in lines
    assert f"{'pytest':<15} {'✅':>8}  {'Test runner (Test Quality)':<40}" in lines
    assert len([l for l in lines if "✅" in l or "❌" in l]) == 11 + 3
    assert f"  ✅ Scanner: {present}" in lines
    assert f"  ❌ Scorer: {tmp_path / 'no-scorer.py'}" in lines
    assert f"  ❌ Gate: {tmp_path / 'no-gate.sh'}" in lines
    rows = [l.split()[0] for l in lines if l[:1].isalpha() and ("✅" in l or "❌" in l)]
    assert rows == sorted(rows) and len(rows) == 11
    assert "-" * 65 in lines
