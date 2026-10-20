#!/usr/bin/env python3
"""Extract raw vocabulary rows from HTML tables, Markdown or CSV/TSV.

This is a parser, not a semantic authority. It preserves questionable rows
instead of guessing repairs. Review its diagnostics before building a ledger.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th"):
            self._buf = []

    def handle_data(self, data: str) -> None:
        self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in ("td", "th") and self._row is not None:
            self._row.append(" ".join("".join(self._buf).split()))
            self._buf = []
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None


ALIASES = {
    "word": {"word", "单词", "词汇", "英文", "term", "spelling"},
    "meaning": {"meaning", "释义", "含义", "中文", "中文释义", "gloss", "definition"},
    "phonetic": {"phonetic", "音标", "pronunciation", "ipa"},
    "index": {"序号", "index", "no", "no.", "id", "编号"},
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def detect_columns(cells: list[str]) -> dict[str, int] | None:
    probes = [norm(c) for c in cells]
    mapping: dict[str, int] = {}
    for field, aliases in ALIASES.items():
        for i, c in enumerate(probes):
            if c in aliases:
                mapping[field] = i
                break
    if "word" in mapping and "meaning" in mapping:
        return mapping
    return None


def guess_columns(cells: list[str]) -> dict[str, int]:
    n = len(cells)
    if n >= 4:
        return {"index": 0, "word": 1, "phonetic": 2, "meaning": 3}
    if n == 3:
        return {"word": 0, "phonetic": 1, "meaning": 2}
    if n == 2:
        return {"word": 0, "meaning": 1}
    return {"word": 0}


def get(cells: list[str], mapping: dict[str, int], key: str) -> str:
    i = mapping.get(key)
    return cells[i].strip() if i is not None and i < len(cells) else ""


def parse_group_label(cells: list[str]) -> str | None:
    text = " ".join(cells).strip()
    if len(cells) <= 2 and re.search(r"\bgroup\b|第\s*\d+\s*组|单元|批次", text, re.I):
        return text
    return None


def rows_from_tables(rows: list[list[str]]) -> list[dict]:
    records = []
    mapping: dict[str, int] | None = None
    group = ""
    for cells in rows:
        label = parse_group_label(cells)
        if label:
            group = label
            continue
        if not cells or not any(c.strip() for c in cells):
            continue
        detected = detect_columns(cells)
        if detected:
            mapping = detected
            continue
        if mapping is None:
            mapping = guess_columns(cells)
        word = get(cells, mapping, "word")
        meaning = get(cells, mapping, "meaning")
        phonetic = get(cells, mapping, "phonetic")
        idx = get(cells, mapping, "index")
        # Keep rows with either a word or a gloss; diagnostics will show blanks.
        if not word and not meaning and not phonetic:
            continue
        # Strip a leading serial like "12." if the source pads it.
        idx = idx.rstrip(".")
        records.append(
            {
                "word": word,
                "phonetic": phonetic,
                "meaning": meaning,
                "source_group": group,
                "source_index": idx,
                "source_note": "",
            }
        )
    return records


def parse_html(text: str) -> list[dict]:
    parser = TableParser()
    parser.feed(text)
    return rows_from_tables(parser.rows)


def parse_markdown(text: str) -> list[dict]:
    # If HTML tables are present, prefer them.
    if re.search(r"<table\b", text, re.I):
        html_rows = parse_html(text)
        if html_rows:
            return html_rows
    rows: list[list[str]] = []
    group = ""
    # Keep group labels as single-cell pseudo-rows so rows_from_tables can see them.
    for line in text.splitlines():
        s = line.strip()
        if re.match(r"^#{1,6}\s*", s):
            header = re.sub(r"^#{1,6}\s*", "", s)
            if re.search(r"\bgroup\b|第\s*\d+\s*组|单元|批次", header, re.I):
                rows.append([header])
            continue
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells if c):
                continue
            rows.append(cells)
    return rows_from_tables(rows)


def parse_delimited(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    delimiter = "\t" if path.suffix.lower() == ".tsv" else ","
    rows = list(csv.reader(text.splitlines(), delimiter=delimiter))
    rows = [[c.strip() for c in row] for row in rows if any(c.strip() for c in row)]
    return rows_from_tables(rows)


def collect(input_path: Path) -> tuple[list[dict], str]:
    suffix = input_path.suffix.lower()
    if suffix in {".html", ".htm"}:
        return parse_html(input_path.read_text(encoding="utf-8")), "html"
    if suffix in {".md", ".markdown", ".txt"}:
        text = input_path.read_text(encoding="utf-8")
        if "<table" in text.lower():
            return parse_html(text), "html-in-markdown"
        return parse_markdown(text), "markdown"
    if suffix in {".csv", ".tsv"}:
        return parse_delimited(input_path), "delimited"
    raise SystemExit(f"暂不支持的文件类型：{suffix}。请提供 .md/.html/.csv/.tsv。")


def main() -> int:
    ap = argparse.ArgumentParser(description="扫描词汇表并输出规范化 CSV（含诊断）")
    ap.add_argument("input", help="原始词表文件")
    ap.add_argument("--out", help="输出 CSV；默认 <input>.words.csv")
    args = ap.parse_args()
    path = Path(args.input).expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"输入文件不存在：{path}")
    records, source_type = collect(path)
    for i, rec in enumerate(records, 1):
        rec["target_id"] = f"R{i:04d}"
        if not rec["word"]:
            rec["source_note"] = "缺少词形，需人工修复"
        elif not rec["meaning"]:
            rec["source_note"] = "缺少释义，需人工修复"
    out = Path(args.out).expanduser() if args.out else path.with_suffix(".words.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    fields = ["target_id", "word", "phonetic", "meaning", "source_group", "source_index", "source_note"]
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    words = [norm(r["word"]) for r in records if r["word"].strip()]
    counts = Counter(words)
    diagnostics = {
        "input": str(path),
        "source_type": source_type,
        "output": str(out),
        "records": len(records),
        "nonempty_unique_words": len(set(words)),
        "duplicate_spellings": [{"word": w, "count": n} for w, n in sorted(counts.items()) if n > 1],
        "missing_word_rows": sum(1 for r in records if not r["word"].strip()),
        "missing_meaning_rows": sum(1 for r in records if not r["meaning"].strip()),
        "missing_phonetic_rows": sum(1 for r in records if not r["phonetic"].strip()),
        "groups": sorted({r["source_group"] for r in records if r["source_group"]}),
        "note": "Diagnostics are raw. Do not treat records or duplicates as final target words until repaired.",
    }
    print(json.dumps(diagnostics, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
