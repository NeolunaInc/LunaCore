from __future__ import annotations

import datetime
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> str:
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        return ""
    return out.stdout.strip()


def gh_json(cmd: list[str]) -> list[dict] | dict | None:
    out = run(cmd)
    if not out:
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


def detect_phase3_status() -> str:
    # default: PR ouverte
    status = "🔄"
    # essaie de lire PR #44
    data = gh_json(["gh", "pr", "view", "44", "--json", "state"])
    if isinstance(data, dict):
        if data.get("state") == "MERGED":
            status = "✅"
        elif data.get("state") == "OPEN":
            status = "🔄"
    return status


def build_backlog_md() -> str:
    issues = gh_json(
        ["gh", "issue", "list", "--state", "open", "--json", "number,title,labels,url"]
    )
    if not isinstance(issues, list):
        return "_Impossible de récupérer les issues (gh non configuré)._"
    lines = ["", "### Backlog (issues ouvertes)", ""]
    lines.append("| # | Titre | Labels | Lien |")
    lines.append("|---:|---|---|---|")
    for it in issues:
        num = it.get("number")
        title = it.get("title", "")
        labels = ",".join([lb.get("name", "") for lb in it.get("labels", [])])
        url = it.get("url", "")
        lines.append(f"| {num} | {title} | {labels} | {url} |")
    return "\n".join(lines) + "\n"


def update_index_md(phase3_status: str) -> None:
    index = ROOT / "docs/PHASES/INDEX.md"
    if not index.exists():
        print("INDEX.md manquant; crée-le d’abord (étape B).", file=sys.stderr)
        return
    text = index.read_text(encoding="utf-8")

    # Replace the table row for Phase 3 status symbol if present
    new_text = text.replace(
        "| 3 | AgentRegistry v1 (Local) | 🔄 |",
        f"| 3 | AgentRegistry v1 (Local) | {phase3_status} |",
    )

    # Append/replace backlog section
    marker = "## Backlog (extrait automatique des issues GitHub)"
    if marker not in new_text:
        # append at end
        new_text = new_text.strip() + "\n\n" + marker + "\n\n"
    # cut existing backlog if present
    head, sep, tail = new_text.partition(marker)
    backlog = build_backlog_md()
    new_text = (
        head
        + marker
        + "\n\n> Généré par `scripts/build_phase_index.py` via `gh` CLI.\n\n"
        + backlog
    )

    index.write_text(new_text, encoding="utf-8")
    print("Updated:", index)


def export_tree_and_zip() -> None:
    export_dir = ROOT / "export"
    export_dir.mkdir(parents=True, exist_ok=True)

    # TREE.files.txt
    files = run(["git", "ls-files"]).splitlines()
    (export_dir / "TREE.files.txt").write_text(
        "\n".join("./" + f for f in files) + "\n", encoding="utf-8"
    )

    # TREE.top.txt
    tops = sorted(
        {(f.split("/")[0] + "/") for f in files if "/" in f}
        | {d + "/" for d in files if "/" not in d}
    )
    (export_dir / "TREE.top.txt").write_text("\n".join(tops) + "\n", encoding="utf-8")

    # ZIP snapshot
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    zip_path = export_dir / f"LunaCore_src_{ts}.zip"
    # use git archive to avoid untracked
    subprocess.run(
        ["git", "archive", "--format=zip", "-o", str(zip_path), "HEAD"], cwd=ROOT, check=True
    )

    # ALL_CODE.txt (concat) — extensions "texte"
    exts = {
        ".py",
        ".md",
        ".yaml",
        ".yml",
        ".json",
        ".toml",
        ".ini",
        ".sh",
        ".txt",
        ".cfg",
        ".env",
        ".rst",
    }
    out_txt = export_dir / "LunaCore_ALL_CODE.txt"
    with out_txt.open("w", encoding="utf-8", newline="\n") as w:
        for f in files:
            p = ROOT / f
            if p.suffix.lower() in exts and p.is_file():
                w.write(f"\n\n##### FILE: {f}\n\n")
                try:
                    w.write(p.read_text(encoding="utf-8"))
                except Exception:
                    w.write("[[binary or unreadable]]")
    print("Exported:", zip_path, "and", out_txt)


def main() -> None:
    status = detect_phase3_status()
    update_index_md(status)
    export_tree_and_zip()


if __name__ == "__main__":
    main()
