---
name: vocab-novel-studio
description: Build, serialize, and audit vocabulary-learning novels or customized short stories from a user-supplied word list or theme. Use this skill whenever the user wants to scan vocabulary data, design a novel framework for word coverage, write the next chapter, generate a personalized short story after a short preference interview, or audit whether target words truly appear in story text. 当用户提到“扫描单词做小说”“词汇小说”“背单词小说”“建立小说总纲”“写下一章”“定制小故事”“短篇词汇故事”“词汇覆盖审计”等任务时，主动使用本 skill。
version: 1.1.2
---

# Vocab Novel Studio · 词汇小说工坊

## Purpose

Turn a user's vocabulary list into a readable long-form novel or a customized short story, while maintaining a traceable mapping from every target word to real story contexts.

The workflow has four modes:

1. **Bootstrap** — scan the word data, audit it, design the novel, allocate all words to chapters.
2. **Continue** — read the project state and write exactly one chapter.
3. **Audit** — verify actual word coverage in existing prose and report problems.
4. **Custom story** — ask a few preference questions, then write a self-contained vocabulary short story.

The guiding rule:

> **Plot is the memory carrier. The target meanings are the knowledge that must survive.**
> Do not sacrifice story for coverage; do not silently drop or misuse words for plot.

## Cold-start contract for public use

This skill is designed for **new, external users**, not as a continuation of the author's private writing project.

1. Do not assume the user's word count, ongoing novel, characters, fandom, language level or earlier drafts.
2. If the workspace contains unrelated vocabulary files, novel drafts or project notes, ignore them unless the user explicitly names them or asks to continue that project.
3. For a custom story, start from the user's own materials: their word list, a topic, a level, or a request for random selection.
4. Never offer options such as “continue my old novel” or “reuse characters from another work” unless the user explicitly brings up that work.
5. Treat “a fresh chat with no existing project” as the default. Existing project data is opt-in only.
6. Do not mention or copy private workspace data into the skill, examples or public artifacts.

If an agent finds private project files while using this public skill, it must not silently treat them as the user's current task.

## Standard project layout

Bundled templates and prompts live next to this `SKILL.md`, under `templates/` and `prompts/`.

### Resolve `<skill-dir>` first

Commands in this document use `<skill-dir>` for the directory containing this `SKILL.md`, because different agent hosts install skills in different places:

- **Claude Code / Claudian:** `.claude/skills/vocab-novel-studio/`
- **DeepSeek Harness (DSH), project:** `.dsh/skills/vocab-novel-studio/`
- **DSH, user-level:** `~/.dsh/skills/vocab-novel-studio/`
- Other hosts: use the actual installed path.

Do not assume the scripts are always under `.claude/skills/...`.

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
        ├── chapters/
        │   └── 第NN章_标题.md
        └── stories/
            └── 日期_故事标题.md
```

`stories/` is optional: use it for one-off or mini-series short stories that do not need a full chapter ledger.

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
python "<skill-dir>/scripts/extract_words.py" <raw-word-list> --out <project>/raw_words.csv
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
python "<skill-dir>/scripts/novel.py" next --novel-dir <project>
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
python "<skill-dir>/scripts/novel.py" audit --novel-dir <project> "<chapter file>"
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

### Mode D · Custom short story or mini-series

Use when the user wants a personalized short story instead of a full serialized novel chapter. This mode may be used without the three project ledgers.

#### D1. Ask only a few questions

For a first-time/external user, start with a neutral version like this (not with options derived from local files):

```text
我可以按你的口味写一篇独立短篇。
先确认三件事：
1. 你有自己的目标词表/主题吗？没有的话，我也可以按难度或主题帮你选词。
2. 想要什么类型/氛围、长度，以及中文/双语/英文？
3. 主角、视角、关系，以及有什么不想看的内容？
```

Do not open with a menu of existing projects, fixed word counts, character reuse, or any option derived from unrelated workspace files. A clean session starts from the user's own inputs.


Ask at most **one short round** of 3–5 high-value questions, and never ask for information the user already provided. If an AskUserQuestion-style tool is available, use it; otherwise ask in plain text.

Core questions:

1. **Target words**: use a list the user supplies, choose from a theme/level, or draw from an existing project ledger? How many?
2. **Genre and mood**: e.g. cozy fantasy, romance, mystery, school, sci-fi, dark fairy tale, healing slice-of-life. Offer 4–6 examples and allow free input.
3. **Length and language**: flash (~800–1,200 Chinese characters), short (~1,500–2,500), or longer (~3,000+); target-word count (8–25); Chinese narration + English target sentences, bilingual, or English-only.
4. **Protagonist and relationship**: original character or user avatar? Desired name, gender, POV, relationships, romance level (none / light / central), and one thing they want to avoid.

Optional:
5. A premise or image the user wants to see; content boundaries; whether to save as a note or reply in chat.

If the user says “随便 / 惊喜 / 你决定”, stop interviewing and choose a coherent default set. Do not interrogate them.

Default when nothing is specified:

- Chinese narrative with English target words;
- gentle fantasy or contemporary magical realism;
- 1,500–2,500 Chinese characters;
- 12–18 target words;
- original protagonist, third-person limited;
- no explicit content; light emotional warmth;
- save to `stories/YYYY-MM-DD_slug.md` if a project exists, otherwise reply in chat.

#### D2. Mirror a tiny custom card

Before writing, show one compact card:

```text
目标词来源 / 数量：
类型 / 氛围：
长度 / 语言：
主角 / 视角：
关系 / 恋爱浓度：
避开的内容：
输出方式：
```

If the user already gave all details, skip the card or show it in one line and proceed.

#### D3. Write a complete short story

- Give it a real arc: want → obstacle → choice → consequence → changed state.
- Include one vivid relationship or emotional turn; not just a word-bearing vignette.
- Put target words into natural English sentences in narration and dialogue. Do not dump them.
- Use each requested target word at least once in the main story; if a word truly cannot fit, say so honestly rather than faking coverage.
- If the story contains an inset reading/exam/quote, words inside it do not count as the main instance; also use them in the main plot.
- Mark first target occurrences in bold; do not over-gloss inside the story.
- Avoid copying recognizable copyrighted characters or plots. A fandom-style mood is fine; the characters and events must be original unless the user owns the material and explicitly asks for fan fiction for private use.

#### D4. End with a light learning layer

Unless the user asks for story-only output, include:

- a compact target-word table (word, actual form, core meaning, story context);
- 2–4 active-recall questions, with answers after a separator;
- coverage note: how many requested words appeared in the main story, and any unused words.

Do not pretend a short story covers a whole word list. State the actual target set.

#### D5. Mini-series continuity

Only if the user wants recurring stories:

- save `stories/` files and a small `short_story_ledger.md` with characters, relationship state, recurring imagery, target words, and unresolved threads;
- read that ledger before the next story;
- do not invent facts that contradict previous stories.

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

For a custom short story:

- title and a one-sentence premise;
- target-word count actually used;
- where it was saved (if anywhere);
- any requested target words that were not used;
- offer a continuation or a new story with the same cast.

Do not paste the whole chapter into chat unless asked; the chapter file is the deliverable.

## Quick prompts

The user can say:

- “用 vocab-novel-studio 扫描这份词表并搭建小说总纲，先不要写正文。”
- “继续词汇小说，写下一章。”
- “审计第 N 章的词汇覆盖。”
- “把模拟阅读里的目标词也补进主线剧情。”
- “给我写一个定制小故事，先问我几个问题。”
- “随便来一个温柔的词汇短篇，12 个目标词。”

If invoked without explicit paths, find the project ledgers first; if multiple projects exist, ask which one.

## Host compatibility

The content is host-agnostic, but automatic discovery is not. Verify the installed skill path before running commands:

- Claude Code / Claudian: `.claude/skills/vocab-novel-studio/`
- DeepSeek Harness: `.dsh/skills/vocab-novel-studio/` (project) or `~/.dsh/skills/vocab-novel-studio/` (user)
- Claude Code bridge for DSH: third-party `dsh-skills-bridge`; not required
- Chat-only hosts: paste/read this file and the relevant prompt; full script-based auditing is unavailable without filesystem and terminal tools

When a host installs the skill in a different directory, resolve the actual skill directory and substitute it for `<skill-dir>`.
