---
name: vocab-novel-studio
description: Build, serialize, and audit long-form vocabulary-learning novels from a user-supplied word list. Use this skill whenever the user wants to scan vocabulary data, design a novel framework for word coverage, write the next chapter of a vocabulary novel, or audit whether target words truly appear in story text. 当用户提到“扫描单词做小说”“词汇小说”“背单词小说”“建立小说总纲”“写下一章”“词汇覆盖审计”等任务时，主动使用本 skill。
version: 1.0.0
---

# Vocab Novel Studio · 词汇小说工坊

## Purpose

Turn a user's vocabulary list into a long-form novel that is readable as fiction first, while maintaining a traceable mapping from every target word to real story contexts.

The workflow has three modes:

1. **Bootstrap** — scan the word data, audit it, design the novel, allocate all words to chapters.
2. **Continue** — read the project state and write exactly one chapter.
3. **Audit** — verify actual word coverage in existing prose and report problems.

The guiding rule:

> **Plot is the memory carrier. The target meanings are the knowledge that must survive.**
> Do not sacrifice story for coverage; do not silently drop or misuse words for plot.

## Standard project layout

Bundled templates and prompts live next to this `SKILL.md`, under `templates/` and `prompts/`.

Prefer this layout unless the user's project already has another one:

```text
<vault>/
├── CLAUDE.md                          # optional project memory
├── .claude/
│   └── skills/
│       └── vocab-novel-studio/        # this skill
└── novels/
    └── <project-slug>/
        ├── 00_novel_bible.md
        ├── 01_vocabulary_ledger.md
        ├── 02_progress_ledger.md
        └── chapters/
            └── 第NN章_标题.md
```

Use the actual paths if the user has an established project. Never overwrite an existing project just to match this template.

## Modes

### Mode A · Bootstrap a new project

Use when there is no framework yet, or the user provides a raw word list.

#### A1. Confirm the actual data

- Read the file the user actually supplied. Do not assume counts from its title.
- Report:
  - number of groups/batches and declared counts;
  - raw rows and unique target words after repairs;
  - duplicates, missing fields, unreadable rows, split rows;
  - whether any batches are missing or undisclosed.
- If data is incomplete, state the gap. Do not invent a number of target words.
- If the source includes an unreliable phonetic column or inconsistent glosses, mark them as needing dictionary verification; do not treat them as authoritative.

Helper:

```bash
python .claude/skills/vocab-novel-studio/scripts/extract_words.py <raw-word-list> --out <project>/raw_words.csv
```

The script is a parser and diagnostic tool, not a full semantic authority. Repair malformed rows explicitly.

#### A2. Design the framework before writing prose

Create `00_novel_bible.md` from `templates/00_novel_bible.md`. Include:

- one-sentence core premise;
- world/history/magic or central rules;
- protagonist ability, limits, goal, flaw, growth;
- main cast with independent motives and arcs;
- relationship plan (not every relationship needs to become romance);
- main plot: beginning, development, major turns, end;
- chapter plan across volumes;
- vocabulary allocation policy;
- memory design;
- quality control.

Do not write chapter prose until the user confirms the framework. If the user explicitly says “directly write”, record that choice.

#### A3. Build the vocabulary ledger

Create `01_vocabulary_ledger.md` using `templates/01_vocabulary_ledger.md`.

For each target word, record at least:

- stable ID (e.g., `W001`);
- spelling and original gloss;
- part(s) of speech / core sense;
- semantic field (preliminary only when the source is thin);
- planned first-appearance chapter;
- candidate recurrence chapters;
- a usage/verification note.

Rules:

- Every target word gets exactly one planned first-appearance chapter.
- Do not claim a word is covered because it is in the ledger.
- Do not assign words only by similar Chinese glosses; verify usage with a dictionary when writing.
- If a word cannot fit its planned chapter naturally, move it within the plan and update the ledger rather than forcing it.
- The ledger must include the total and distinguish “planned” from “covered in prose”.

#### A4. Set up the progress ledger and project memory

Create `02_progress_ledger.md` from the template.

If appropriate, create a project-level `CLAUDE.md` that tells future sessions:

- where the project lives;
- which skill to use;
- the exact coverage rules;
- the current next chapter.

Do not put private word-list data or novel prose in a public repository without the user's explicit consent.

### Mode B · Continue with the next chapter

Use when a project already has a bible, a vocabulary ledger and a progress ledger.

#### B1. Preflight

Run:

```bash
python .claude/skills/vocab-novel-studio/scripts/novel.py next --novel-dir <project>
```

Then read:

- the latest progress record;
- the previous chapter's ending and its continuity notes;
- the relevant volume/chapter entry in the bible;
- the next chapter's assigned word block in the vocabulary ledger.

Determine:

- previous events;
- current time/place/injuries/relationships/secrets;
- next chapter's first-appearance words;
- 6–10 old words to recur naturally;
- the chapter's dramatic goal, event and hook.

If the progress ledger and actual files disagree, repair the ledger before writing.

#### B2. Write one chapter only

Default length: 4,500–6,500 Chinese characters plus the end-of-chapter learning modules, unless the user specifies otherwise.

Hard requirements:

- Every first-appearance target word appears in at least one **main-plot** instance: action, dialogue, a decision, or a visible consequence.
- Every recurrence word used must be natural to the scene.
- English must be grammatical and idiomatic; target words live inside complete sentences, not lists.
- A chapter has a clear goal, meaningful character interaction, a change, and a hook.
- Do not sacrifice characterization for word coverage.
- Do not turn the novel into a textbook. Use context before explanation.
- **Inset rule:** words appearing only in a mock reading, exam passage, letter, inscription, quotation or other inset text do **not** count as the chapter's primary coverage. Each such word needs a separate main-plot instance.

Mark inset material:

```markdown
<!-- inset:start -->
...
<!-- inset:end -->
```

Markdown blockquote lines are also treated as inset by the audit script.

#### B3. Chapter format

Use `templates/chapter_template.md`. Minimum sections:

- frontmatter (`book`, `chapter`, `title`, `status`, `targets`);
- Chinese narrative body;
- `# 章末记忆模块`;
- A. plot recap;
- B. target-word list with actual forms and contexts;
- C. memory hooks (clearly distinguish verified etymology from mnemonic association);
- D. active recall questions, then a separate answer area;
- E. coverage report.

#### B4. Audit and update

Run:

```bash
python .claude/skills/vocab-novel-studio/scripts/novel.py audit --novel-dir <project> "<chapter file>"
```

The script is a first-pass word-form check. Still verify every target word manually for:

- grammar and collocation;
- semantic fit;
- whether it is a near-form of another word;
- whether its only occurrence is in an inset;
- whether the chapter's B/E tables match the prose.

Update:

- `02_progress_ledger.md`: chapter status, actual first coverage, recurrence count, continuity facts, next-chapter state;
- `01_vocabulary_ledger.md` header progress, if that is the project's convention;
- `00_novel_bible.md` only for material setting/structure changes.

Do not mark coverage that has not been verified.

### Mode C · Audit existing chapters

Use when the user asks for a coverage audit. Read the actual chapter files, not only summaries.

For every target word, classify:

- **Covered** — accurate, natural instance in prose; if the primary context is an inset, verify a separate plot instance.
- **Appeared but needs improvement** — word appears, but grammar, collocation, semantic clarity or memory context is insufficient.
- **Not covered** — no valid instance.
- **Unverified** — data/context missing.

Report scope, chapter/file evidence, actual forms, problems, repair suggestions, counts and whether the audit is full or partial. Never inflate coverage.

## Non-negotiable quality rules

1. Target words must be accurate. A similar Chinese gloss does not prove two English words are interchangeable.
2. Do not invent etymologies. Mark mnemonics as mnemonics.
3. Inflected forms of the same target lexeme may count, but record the actual form. Derivational forms and near-homographs do not automatically count for a different target.
4. Word lists, headings, memory hints and answer keys do not count as prose coverage.
5. A novel can be dark or romantic; characters still need agency. Do not use a harem/reward structure to avoid giving side characters goals.
6. Do not overuse amnesia, prophecy or coincidence as plot glue.
7. Keep a living continuity record. Do not rely on chat memory across sessions.
8. Do not make the number of words a chapter can hold exceed what the story can support. A smaller, natural chapter is better than a stuffed one.
9. If the user prefers a different language pair than Chinese/English, preserve the same workflow but do not force English target sentences.
10. Public sharing of source word lists and novel text requires the user's permission and respect for copyright.

## Scripts

### `extract_words.py`

Parses HTML tables, Markdown tables or CSV/TSV word data and outputs a normalized CSV plus diagnostics. It does not repair semantic errors automatically.

### `novel.py`

- `next --novel-dir <project>` — read the ledger and latest chapter file; print next chapter title, target words, recurrence candidates and progress.
- `audit --novel-dir <project> <chapter>` — preliminary form/coverage audit; excludes inset text and reports missing/inset-only/extra target words.

The scripts use standard library only. Treat their output as a checklist, not as the final judge.

## Output to the user

For a newly written chapter:

- link/path to the chapter;
- one-sentence plot summary;
- first-coverage count, cumulative coverage and recurrence count;
- the real unresolved hook;
- what state the next chapter starts from;
- ask whether to continue.

Do not paste the whole chapter into chat unless asked; the chapter file is the deliverable.

## Quick prompts

The user can say:

- “用 vocab-novel-studio 扫描这份词表并搭建小说总纲，先不要写正文。”
- “继续词汇小说，写下一章。”
- “审计第 N 章的词汇覆盖。”
- “把模拟阅读里的目标词也补进主线剧情。”

If invoked without explicit paths, find the project ledgers first; if multiple projects exist, ask which one.
