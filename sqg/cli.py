#!/usr/bin/env python3
"""SQG CLI: Saffron Quality Gate command-line interface."""
import argparse, json, os, subprocess, sys, textwrap

__version__ = "1.0.0"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HERMES_SCRIPTS = os.path.expanduser("~/.hermes/scripts")
SCANNER = os.path.join(HERMES_SCRIPTS, "saffron-anti-slop-scanner.py")
SCORER = os.path.join(HERMES_SCRIPTS, "saffron-dimension-scorer.py")
GATE = os.path.join(HERMES_SCRIPTS, "saffron-gate-runner.sh")

LOGO = """
╔══════════════════════════════════════════════╗
║   SAFFRON QUALITY GATE                       ║
║   An executable quality gate for code,       ║
║   content and configuration.                 ║
╚══════════════════════════════════════════════╝
"""


def cmd_exists(name):
    return subprocess.run(["which", name], capture_output=True).returncode == 0


def run_tool(tool_path, args, timeout=120):
    """Run a tool and return (returncode, stdout, stderr)."""
    if not os.path.exists(tool_path):
        return -1, "", f"tool not found: {tool_path}"
    try:
        r = subprocess.run(
            [sys.executable, tool_path] + args,
            capture_output=True, text=True, timeout=timeout
        )
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except FileNotFoundError:
        return -1, "", "python not found"


def cmd_scan(args):
    """sqg scan --path <dir> [--format json|table|summary] [--strict]"""
    fmt_args = ["--format", args.format]
    if args.strict:
        fmt_args.append("--strict")
    rc, out, err = run_tool(SCANNER, ["--path", args.path] + fmt_args)
    print(out if out else err)
    return rc


def cmd_audit(args):
    """sqg audit --path <dir> [--format json|table] [--strict]"""
    fmt_args = ["--format", args.format]
    if args.strict:
        fmt_args.append("--strict")
    rc, out, err = run_tool(SCORER, ["--path", args.path] + fmt_args)
    print(out if out else err)
    return rc


def cmd_gate(args):
    """sqg gate --path <dir> [--strict]"""
    if not os.path.exists(GATE):
        print("Gate runner not found — run `sqg scan` or `sqg audit` directly.")
        return 1
    flags = ""
    if args.strict:
        flags += " --strict"
    r = subprocess.run(["bash", GATE, args.path, flags], text=True, timeout=180)
    print(r.stdout or "")
    return r.returncode


def cmd_check(args):
    """sqg check — check which tools are installed."""
    tools = {
        "ruff": "Code linting (Correctness)",
        "mypy": "Type checking (Correctness)",
        "bandit": "Security scanning (Security)",
        "semgrep": "Pattern scanning (Security)",
        "mutmut": "Mutation testing (Test Quality)",
        "pytest": "Test runner (Test Quality)",
        "pa11y": "Accessibility audit",
        "vale": "Prose quality (Documentation)",
        "eslint": "JS/TS linting (Maintainability)",
        "prettier": "Code formatting (Maintainability)",
        "lighthouse": "Web performance (Performance)",
    }
    print(f"{LOGO}")
    print(f"SQG v{__version__} — Environment Check\n")
    print(f"{'Tool':<15} {'Status':>8}  {'Purpose':<40}")
    print("-" * 65)
    for tool, purpose in sorted(tools.items()):
        status = "✅" if cmd_exists(tool) else "❌"
        print(f"{tool:<15} {status:>8}  {purpose:<40}")
    print()
    print(f"Core scripts:")
    for name, path in [("Scanner", SCANNER), ("Scorer", SCORER), ("Gate", GATE)]:
        status = "✅" if os.path.exists(path) else "❌"
        print(f"  {status} {name}: {path}")
    return 0


def cmd_version(args):
    """sqg version"""
    print(f"SQG v{__version__}")
    print("Saffron Quality Gate: an executable quality gate for code, content and configuration.")
    print("© Saffron · saffronsystems.io")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="sqg",
        description="Saffron Quality Gate: executable quality enforcement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              sqg scan --path .                     Anti-slop scan (default: table)
              sqg scan --path . --format json        Machine-readable output
              sqg audit --path .                     Full 14-dimension quality audit
              sqg gate --path .                      Unified gate pipeline
              sqg check                              Check tool installation status
              sqg version                            Version info
            Commands:
              scan    Run anti-slop pattern scanner (A-001 through A-036)
              audit   Run full 14-dimension quality audit
              gate    Run unified quality gate pipeline
              check   Check installed tool status
              version Show version information
        """),
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit")

    subparsers = parser.add_subparsers(dest="command")

    # scan
    p_scan = subparsers.add_parser("scan", help="Run anti-slop pattern scanner")
    p_scan.add_argument("--path", "-p", default=".", help="File or directory to scan")
    p_scan.add_argument("--format", "-f", choices=["json", "table", "summary"], default="table")
    p_scan.add_argument("--strict", action="store_true", help="Fail on warnings")

    # audit
    p_audit = subparsers.add_parser("audit", help="Run full quality audit")
    p_audit.add_argument("--path", "-p", default=".", help="File or directory to audit")
    p_audit.add_argument("--format", "-f", choices=["json", "table"], default="table")
    p_audit.add_argument("--strict", action="store_true", help="Fail below Grade A")

    # gate
    p_gate = subparsers.add_parser("gate", help="Run unified quality gate pipeline")
    p_gate.add_argument("--path", "-p", default=".", help="File or directory to gate")
    p_gate.add_argument("--strict", action="store_true", help="Fail on warnings")

    # check
    subparsers.add_parser("check", help="Check tool installation status")

    # version
    subparsers.add_parser("version", help="Show version information")

    args = parser.parse_args()

    if args.version or (hasattr(args, 'command') and args.command is None and not hasattr(args, 'command')):
        parser.print_help()
        return 0

    if args.command == "scan":
        sys.exit(cmd_scan(args))
    elif args.command == "audit":
        sys.exit(cmd_audit(args))
    elif args.command == "gate":
        sys.exit(cmd_gate(args))
    elif args.command == "check":
        sys.exit(cmd_check(args))
    elif args.command == "version":
        sys.exit(cmd_version(args))
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    main()