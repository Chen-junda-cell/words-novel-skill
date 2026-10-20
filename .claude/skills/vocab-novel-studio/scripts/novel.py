#!/usr/bin/env python3
"""Vocabulary-novel preflight and preliminary coverage audit.

Standard library only. The output is a checklist, not a substitute for
word-by-word human review of meaning, grammar and narrative context.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BIBLE = "00_novel_bible.md"
LEDGER = "01_vocabulary_ledger.md"
PROGRESS = "02_progress_ledger.md"
CHAPTER_DIR = "chapters"


def resolve_project(value: str) -> Path:
    p = Path(value).expanduser().resolve()
    if not (p / LEDGER).exists():
        raise SystemExit(f"找不到词汇台账：{p / LEDGER}")
    return p


def parse_ledger(project: Path) -> dict[int, dict]:
    text = (project / LEDGER).read_text(encoding="utf-8")
    headings = list(re.finditer(r"^##\s*第\s*(\d+)\s*章\s*[·:：-]\s*(.+?)\s*$", text, re.M))
    chapters: dict[int, dict] = {}
    for i, match in enumerate(headings):
        n = int(match.group(1))
        title = match.group(2).strip()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        block = text[match.end():end]
        targets = []
        for line in block.splitlines():
            if not line.lstrip().startswith("| W"):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            wid = cells[0]
            word = cells[1].replace("*", "").strip()
            if not re.fullmatch(r"W\d{3,}", wid) or not word:
                continue
            targets.append(
                {
                    "id": wid,
                    "word": word,
                    "gloss": cells[2],
                    "semantic_field": cells[3] if len(cells) > 3 else "",
                    "recurrence": cells[4] if len(cells) > 4 else "",
                    "notes": cells[5] if len(cells) > 5 else "",
                }
            )
        chapters[n] = {"title": title, "targets": targets}
    if not chapters:
        raise SystemExit("词汇台账中没有找到 '## 第N章 · 标题' 章节。请先按模板建立分配表。")
    return chapters


def parse_progress(project: Path) -> dict[str, str]:
    path = project / PROGRESS
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    out = {}
    for key in ("已写章节", "正文已覆盖目标词", "正文复现实例", "最近更新"):
        m = re.search(rf"^\|\s*{re.escape(key)}\s*\|\s*([^|]+?)\s*\|", text, re.M)
        if m:
            out[key] = m.group(1).strip()
    return out


def chapter_files(project: Path) -> list[tuple[int, Path]]:
    folder = project / CHAPTER_DIR
    if not folder.exists():
        folder = project
    files = []
    for path in folder.glob("第*章_*.md"):
        m = re.match(r"第(\d+)章_", path.name)
        if m:
            files.append((int(m.group(1)), path))
    return sorted(files)


def forms(word: str) -> set[str]:
    """Rough regular/irregular forms for first-pass matching."""
    w = word.lower().strip()
    out = {w}
    if w.endswith("e"):
        out |= {w + "d", w + "s", w[:-1] + "ing", w[:-1] + "ed"}
    elif w.endswith("y") and len(w) > 2:
        out |= {w[:-1] + "ies", w[:-1] + "ied", w + "s", w[:-1] + "ier", w[:-1] + "iest"}
    else:
        out |= {w + "s", w + "ed", w + "ing", w + "er", w + "est"}
        if (
            len(w) > 3
            and w[-1] not in "aeiou"
            and w[-2] in "aeiou"
            and w[-3] not in "aeiou"
        ):
            out |= {w + w[-1] + "ed", w + w[-1] + "ing", w + w[-1] + "er", w + w[-1] + "est"}
    irregular = {
        "withdraw": {"withdrew", "withdrawn"},
        "withstand": {"withstood"},
        "mislead": {"misled"},
        "foresee": {"foresaw", "foreseen"},
        "creep": {"crept"},
        "strive": {"strove", "striven"},
        "swing": {"swung"},
        "shed": {"shed"},
        "burst": {"burst"},
    }
    return out | irregular.get(w, set())


def words_in(text: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'-]*", text)}


def split_body(text: str) -> tuple[str, str]:
    """Return (main prose, inset text). Excludes rules, modules and insets."""
    if text.startswith("---"):
        m = re.match(r"^---\s*\n.*?\n---\s*\n", text, re.S)
        if m:
            text = text[m.end():]
    for marker in ("\n# 章末记忆模块", "\n# 章末记忆", "\n## A. 本章剧情回顾", "\n# Chapter-end memory module"):
        if marker in text:
            text = text.split(marker, 1)[0]
            break
    inset_parts = []

    def take_marked(match: re.Match) -> str:
        inset_parts.append(match.group(1))
        return " "

    primary = re.sub(
        r"<!--\s*inset:start\s*-->(.*?)<!--\s*inset:end\s*-->",
        take_marked,
        text,
        flags=re.S | re.I,
    )
    lines = []
    for line in primary.splitlines():
        if re.match(r"^\s*>", line):
            inset_parts.append(line)
            lines.append("")
        else:
            lines.append(line)
    return "\n".join(lines), "\n".join(inset_parts)


def cmd_next(project: Path) -> int:
    chapters = parse_ledger(project)
    files = chapter_files(project)
    latest_num = files[-1][0] if files else 0
    latest_file = files[-1][1] if files else None
    next_num = latest_num + 1
    progress = parse_progress(project)
    warning = None
    m = re.search(r"(\d+)\s*/\s*(\d+)", progress.get("已写章节", ""))
    if m and int(m.group(1)) != latest_num:
        warning = f"进度台账写已写 {m.group(1)} 章，但实际找到 {latest_num} 章；请先核对。"
    if next_num not in chapters:
        print(json.dumps({"error": f"词汇台账中没有第 {next_num} 章", "warning": warning}, ensure_ascii=False, indent=2))
        return 1
    plan = chapters[next_num]
    recurrence_candidates = []
    for cnum, ch in chapters.items():
        if cnum >= next_num:
            continue
        for t in ch["targets"]:
            windows = [int(x) for x in re.findall(r"第\s*(\d+)\s*章", t.get("recurrence", ""))]
            if next_num in windows:
                recurrence_candidates.append(
                    {
                        "id": t["id"],
                        "word": t["word"],
                        "gloss": t["gloss"],
                        "first_chapter": cnum,
                        "candidate_windows": t.get("recurrence", ""),
                    }
                )
    total_words = len({t["word"].lower() for ch in chapters.values() for t in ch["targets"]})
    data = {
        "project": str(project),
        "latest_written_chapter": latest_num,
        "latest_chapter_file": str(latest_file) if latest_file else None,
        "next_chapter": next_num,
        "title": plan["title"],
        "target_count": len(plan["targets"]),
        "targets": plan["targets"],
        "recurrence_candidates": recurrence_candidates,
        "total_unique_targets": total_words,
        "progress": progress,
        "warning": warning,
        "rule": "First-appearance target words need a main-plot instance. Words that appear only in inset text (mock reading, exam, letter, inscription, quote) do not count as primary coverage.",
        "note": "This is plan data, not verified prose coverage.",
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


def cmd_audit(project: Path, chapter_value: str) -> int:
    chapters = parse_ledger(project)
    chapter_path = Path(chapter_value).expanduser()
    if not chapter_path.is_absolute():
        cwd_candidate = (Path.cwd() / chapter_path).resolve()
        project_candidate = (project / chapter_path).resolve()
        chapter_path = cwd_candidate if cwd_candidate.exists() else project_candidate
    if not chapter_path.exists():
        print(json.dumps({"error": f"章节文件不存在：{chapter_path}"}, ensure_ascii=False, indent=2))
        return 1
    m = re.match(r"第(\d+)章_", chapter_path.name)
    if not m:
        print(json.dumps({"error": "章节文件名应符合 第NN章_标题.md"}, ensure_ascii=False, indent=2))
        return 1
    n = int(m.group(1))
    plan = chapters.get(n)
    if not plan:
        print(json.dumps({"error": f"词汇台账中没有第 {n} 章"}, ensure_ascii=False, indent=2))
        return 1
    primary, inset = split_body(chapter_path.read_text(encoding="utf-8"))
    primary_tokens = words_in(primary)
    inset_tokens = words_in(inset)
    assigned = plan["targets"]
    assigned_ids = {t["id"] for t in assigned}
    rows, primary_count, inset_only, missing = [], 0, [], []
    for t in assigned:
        fs = forms(t["word"])
        p_forms = sorted(fs & primary_tokens)
        i_forms = sorted(fs & inset_tokens)
        if p_forms:
            status = "PRIMARY"
            primary_count += 1
        elif i_forms:
            status = "INSET_ONLY"
            inset_only.append(t["id"])
        else:
            status = "MISSING"
            missing.append(t["id"])
        rows.append(
            {
                "id": t["id"],
                "word": t["word"],
                "status": status,
                "primary_forms": p_forms,
                "inset_forms": i_forms,
            }
        )
    all_targets = [(c, t) for c, ch in chapters.items() for t in ch["targets"]]
    extra = []
    for cnum, t in all_targets:
        if t["id"] in assigned_ids:
            continue
        hits = sorted(forms(t["word"]) & primary_tokens)
        if hits:
            extra.append({"id": t["id"], "word": t["word"], "forms": hits, "planned_chapter": cnum})
    total_words = len({t["word"].lower() for _, t in all_targets})
    data = {
        "project": str(project),
        "chapter": n,
        "title": plan["title"],
        "file": str(chapter_path),
        "body_chinese_chars": len(re.findall(r"[一-鿿]", primary + "\n" + inset)),
        "assigned_targets": len(assigned),
        "primary_coverage": primary_count,
        "inset_only": inset_only,
        "missing": missing,
        "extra_target_occurrences": extra,
        "targets": rows,
        "total_unique_targets": total_words,
        "note": "Preliminary form check only. Manually verify meaning, grammar, collocation, near-homographs and inset-vs-plot coverage.",
    }
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0 if not missing and not inset_only else 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Vocabulary-novel preflight and coverage audit")
    sub = parser.add_subparsers(dest="command", required=True)
    p_next = sub.add_parser("next", help="下一章预检")
    p_next.add_argument("--novel-dir", required=True, help="项目目录（含 01_vocabulary_ledger.md）")
    p_audit = sub.add_parser("audit", help="章节词形初审")
    p_audit.add_argument("--novel-dir", required=True, help="项目目录（含 01_vocabulary_ledger.md）")
    p_audit.add_argument("chapter", help="章节文件路径")
    args = parser.parse_args()
    project = resolve_project(args.novel_dir)
    if args.command == "next":
        return cmd_next(project)
    return cmd_audit(project, args.chapter)


if __name__ == "__main__":
    raise SystemExit(main())
