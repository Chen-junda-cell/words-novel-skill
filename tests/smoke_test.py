#!/usr/bin/env python3
"""Small end-to-end smoke test for the bundled scripts.

Run from the repository root:
    python tests/smoke_test.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOVEL = ROOT / ".claude" / "skills" / "vocab-novel-studio" / "scripts" / "novel.py"
EXTRACT = ROOT / ".claude" / "skills" / "vocab-novel-studio" / "scripts" / "extract_words.py"


def run(args: list[str], cwd: Path, expect: int | None = None) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [sys.executable, *args],
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        capture_output=True,
        env=env,
    )
    if expect is not None and proc.returncode != expect:
        raise AssertionError(
            f"expected exit {expect}, got {proc.returncode}\n"
            f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
        )
    return proc


def write_test_project(root: Path) -> Path:
    project = root / "novel"
    (project / "chapters").mkdir(parents=True)
    (project / "01_vocabulary_ledger.md").write_text(
        """# Test ledger

## 第1章 · 第一场

| 词汇ID | 目标词 | 原表释义 | 语义场 | 后续候选复现 | 备注 |
|---|---|---|---|---|---|
| W001 | **abide** | v. 遵守 | 伦理 | 第2章 | test |
| W002 | **absorb** | v. 吸收 | 通用 | 第2章 | test |

## 第2章 · 第二场

| 词汇ID | 目标词 | 原表释义 | 语义场 | 后续候选复现 | 备注 |
|---|---|---|---|---|---|
| W003 | **accelerate** | v. 加速 | 变化 | 第3章 | test |
""",
        encoding="utf-8",
    )
    (project / "02_progress_ledger.md").write_text(
        """# 进度

| 指标 | 当前值 | 说明 |
|---|---:|---|
| 已写章节 | 1 / 2 | test |
| 正文已覆盖目标词 | 1 / 3 | test |
| 正文复现实例 | 0 | test |
| 最近更新 | 2026-01-01 | test |
""",
        encoding="utf-8",
    )
    (project / "chapters" / "第01章_第一场.md").write_text(
        """---
book: test
chapter: 1
title: 第一场
targets:
  - abide
  - absorb
---

# 第1章 · 第一场

> 模拟阅读：The old rule says we must **abide** by the law.

The blank page **absorbed** the ink, and nothing else happened.

# 章末记忆模块

## A. 本章剧情回顾

test
""",
        encoding="utf-8",
    )
    return project


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="vocab_novel_smoke_") as tmp:
        root = Path(tmp)
        project = write_test_project(root)

        next_proc = run(
            [str(NOVEL), "next", "--novel-dir", str(project)], root, expect=0
        )
        next_data = json.loads(next_proc.stdout)
        assert next_data["next_chapter"] == 2, next_data
        assert next_data["title"] == "第二场", next_data
        assert next_data["target_count"] == 1, next_data

        audit_proc = run(
            [
                str(NOVEL),
                "audit",
                "--novel-dir",
                str(project),
                str(project / "chapters" / "第01章_第一场.md"),
            ],
            root,
            expect=2,
        )
        audit_data = json.loads(audit_proc.stdout)
        assert audit_data["primary_coverage"] == 1, audit_data
        assert audit_data["inset_only"] == ["W001"], audit_data
        assert audit_data["missing"] == [], audit_data

        chapter = project / "chapters" / "第01章_第一场.md"
        chapter.write_text(
            chapter.read_text(encoding="utf-8").replace(
                "The blank page **absorbed** the ink, and nothing else happened.",
                "The blank page **absorbed** the ink, and she chose to **abide** by the old rule.",
            ),
            encoding="utf-8",
        )
        fixed_proc = run(
            [
                str(NOVEL),
                "audit",
                "--novel-dir",
                str(project),
                str(chapter),
            ],
            root,
            expect=0,
        )
        fixed_data = json.loads(fixed_proc.stdout)
        assert fixed_data["primary_coverage"] == 2, fixed_data
        assert fixed_data["inset_only"] == [], fixed_data

        raw = root / "raw.md"
        raw.write_text(
            """| 序号 | 单词 | 音标 | 含义 |
|---|---|---|---|
| 1. | abide | [ə'baɪd] | v. 遵守 |
| 2. | absorb | [əb'sɔːb] | v. 吸收 |
""",
            encoding="utf-8",
        )
        csv_path = root / "raw_words.csv"
        extract_proc = run([str(EXTRACT), str(raw), "--out", str(csv_path)], root, expect=0)
        diag = json.loads(extract_proc.stdout)
        assert diag["records"] == 2, diag
        assert diag["nonempty_unique_words"] == 2, diag
        assert csv_path.exists(), diag

        print("SMOKE TEST PASSED")
        print(json.dumps({"next": next_data["title"], "audit": fixed_data["primary_coverage"], "extracted": 2}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
