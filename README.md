# Vocab Novel Studio · 词汇小说工坊

把一份单词表变成一部能长期连载的轻小说，或先经过几轮问答，生成一篇专属于你的词汇短篇故事；同时持续追踪目标词到底有没有真正进入故事。

这是一个面向 **Claude Code、DeepSeek Harness（DSH）以及兼容 Agent Skills 的客户端** 的项目级 skill。它组合了：

- 词表扫描与数据质量检查；
- 小说世界观、人物、章节和词汇分配总纲；
- 单章创作引擎；
- 逐词覆盖审计；
- 连续性与记忆进度台账；
- “模拟阅读不能单独算覆盖”的硬规则；
- 先询问偏好、再生成定制小故事的互动模式；
- 可打包成 Obsidian Vault 压缩包，并提供新对话续写上下文。

> 仓库只提供工作流、脚本和模板。**不包含任何用户的小说正文、角色设定或受版权保护的原始词表。**

---

## 为什么需要它

AI 写词汇小说时很容易出现三种失败：

1. 写着写着忘记目标词；
2. 在章末词表里“解释过”就当作正文已经使用；
3. 为了塞词牺牲人物、剧情和英语自然度。

这个 skill 把“计划覆盖”和“正文覆盖”分开，强制先读进度、写一章、逐词审计、再更新台账。

---

## 功能

### 1. Bootstrap：从词表建立小说项目

- 解析 HTML 表格、Markdown 表格、CSV/TSV；
- 报告原始行数、可识别词数、重复项、缺失字段；
- 设计 A–J 创作总纲；
- 为每个目标词分配计划首现章节与复现窗口；
- 未确认框架前不自动写正文。

### 2. Continue：续写下一章

- 读取上一章与进度台账；
- 找出下一章的 15–25 个（可配置）首现目标词；
- 选择适合本章自然复现的旧词；
- 生成一章中文轻小说 + 英语目标词语境；
- 生成 A–E 章末记忆模块；
- 自动更新覆盖与连续性记录。

### 3. Audit：严格覆盖审计

- 区分正文、词表、记忆钩子、答案区；
- 排除模拟阅读、试卷、引文等 inset 文本；
- 对每个目标词报告：已覆盖 / 已出现但需改进 / 未覆盖 / 待核验；
- 不虚报覆盖率。

### 4. Custom Story：问答后生成定制短篇

- Agent 先问 3–5 个关键问题：目标词、类型氛围、长度、主角关系、内容边界；
- 如果用户说“随便”，使用默认组合，不再盘问；
- 支持一次性短篇，也支持同一组人物的迷你连载；
- 输出完整故事弧线，而不是词汇展示片段；
- 目标词进入自然英文句子，篇末附轻量词汇回声与可选主动回忆。

### 5. Portable Vault：打包到 Obsidian

- 把故事、人物/连续性文件、词汇回声打包成单个 zip；
- 解压后得到一个顶层 Vault 文件夹，用 Obsidian 的 **Open folder as vault** 直接打开；
- 同时生成 `RESUME_CONTEXT.md`，可粘贴或附加到新对话继续写；
- 自动排除 `.env`、`.git`、`.obsidian`、缓存和 `data/raw/`。

### 6. Resume：新对话继续写

- 打包时同时生成 `RESUME_CONTEXT.md` 和 `CONTINUE_HERE.md`；
- 新对话里附上/粘贴 `RESUME_CONTEXT.md`，agent 就能从上次停下的位置继续；
- 不依赖上一段聊天记录，也不会擅自重新开始；
- 如果没有终端或 Python，agent 应明确说明 zip 无法生成，而不是假装已经生成。

### 7. 用户附加硬规则

> 模拟阅读、试卷、信件、碑文或引文中的目标词，必须在同一章主线动作、对话或后果中再出现一次，才能算主覆盖。

内嵌文本可以用下方标记包裹：

```markdown
<!-- inset:start -->
...
<!-- inset:end -->
```

Markdown 引用行也会被审计脚本视为 inset。

---

## 安装

### 方式 A：直接把本仓库当作工作目录

```bash
git clone <your-repo-url> vocab-novel-studio
cd vocab-novel-studio
```

用支持项目 skills 的 Claude Code/Claudian 打开该目录。`.claude/skills/vocab-novel-studio/` 会被发现。

### 方式 B：复制到现有 Vault

把本仓库的：

```text
.claude/skills/vocab-novel-studio/
```

整个复制到你的 Vault 的：

```text
<Vault>/.claude/skills/vocab-novel-studio/
```

模板与 prompts 已经打包在这个 skill 目录内，不需要另外复制。再把其中 `templates/project_CLAUDE.md` 复制为项目记忆 `CLAUDE.md`，按你的小说名修改。

### 方式 C：DeepSeek Harness（DSH）

DSH 原生支持 `SKILL.md`，但它扫描的是 `.dsh/skills/`，不是 `.claude/skills/`。推荐在项目根目录安装：

```powershell
New-Item -ItemType Directory -Force -Path .dsh\skills
Copy-Item -Recurse -Force .claude\skills\vocab-novel-studio .dsh\skills\
```

也可以安装到用户级：

```powershell
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.dsh\skills"
Copy-Item -Recurse -Force .claude\skills\vocab-novel-studio "$env:USERPROFILE\.dsh\skills\"
```

然后在 DSH 中直接说“用 vocab-novel-studio 给我写一个定制小故事，先问我几个问题”，或尝试 `/vocab-novel-studio`。

> 如果 DSH 读取到了当前主 Vault 里的其他项目，它可能会把这些项目当成用户上下文。测试“其他用户”的体验时，请在只包含 `vocab-novel-studio` 仓库的干净目录中启动 DSH；或明确发送 `prompts/00-start-here.md` 里的冷启动指令。

> DSH 是开发者预览版，技能目录与加载行为以你安装的版本为准；它需要文件系统和终端工具才能运行 Python 审计脚本。

> 如果使用第三方 `dsh-skills-bridge`，也可以把 Claude Code 技能目录桥接进 DSH。桥接插件不是本仓库依赖。

### 发布到 GitHub

在 GitHub 创建一个空仓库（不要初始化 README），然后在本目录执行：

```bash
git remote add origin <your-repo-url>
git push -u origin main
```

当前打包版本已经在本地初始化并提交；如果仓库设为 Public，请确认不要提交自己的词表、小说正文或个人信息。

### 要求

- Python 3.11+（脚本只使用标准库）
- 支持 Agent Skills 的 Claude Code / Claudian 或 DeepSeek Harness
- 完整流程需要文件读写与终端执行能力；纯聊天界面只能使用定制短篇的提示流程
- Obsidian 可选，但适合作为长期写作与阅读界面

---

## 只想写一篇定制小故事？

不需要先建立长篇项目。直接对 Agent 说：

```text
用 vocab-novel-studio 给我写一个定制小故事。
先问我几个问题，再开始写。
```

### 给外部用户：冷启动规则

这个技能面向所有用户，不依赖作者的私人小说、词表或角色。测试全新用户体验时，最稳的是在一个**只包含本仓库的干净目录**里启动 agent；不要在主 Vault 中让 agent 读到无关的小说项目和旧稿。

也可以在第一次消息里直接加上：

```text
请把我看成第一次使用这个 skill 的新用户。
不要读取或引用当前工作区里与我的请求无关的小说、词表、角色或进度文件。
先问我最多 3 个问题，再开始写。
```

对应的冷启动文件：`.claude/skills/vocab-novel-studio/prompts/00-start-here.md`。

例如它可能会问：

- 目标词用你提供的词表，还是围绕某个主题选？
- 想要温柔奇幻、悬疑、校园、科幻，还是别的氛围？
- 想要 800–1,200 字、1,500–2,500 字，还是更长？
- 主角是谁，视角和恋爱浓度如何，有什么不想看的内容？

如果你只想省事，也可以说：

```text
随便来一个温柔的短篇，12 个目标词，不要问我太多。
```

详细问答与生成规范见 `.claude/skills/vocab-novel-studio/prompts/04-custom-short-story.md`。

### 新对话接着续写

解压或打包后，在新对话里发：

```text
读取我附上的 RESUME_CONTEXT.md 和最新故事文件。
从上次停下的位置继续，不要重新开始，也不要改掉已有人物关系。
```

如果 agent 不能直接读取 Markdown，就把 `RESUME_CONTEXT.md` 的内容直接粘贴进对话。

---

## 快速开始：建立长篇项目

### 1. 创建小说项目目录

```text
novels/<your-novel>/
├── 00_novel_bible.md
├── 01_vocabulary_ledger.md
├── 02_progress_ledger.md
└── chapters/
```

从 `.claude/skills/vocab-novel-studio/templates/` 复制 `00`、`01`、`02`，按你的书名和读法填写。

### 2. 准备词表

把原始词表放到任意位置，例如：

```text
data/my-word-list.md
```

支持：

- HTML 表格（也可以嵌在 Markdown 中）
- Markdown 管道表格
- CSV
- TSV

先运行扫描器：

```bash
python .claude/skills/vocab-novel-studio/scripts/extract_words.py \
  data/my-word-list.md \
  --out data/raw_words.csv
```

它会输出 CSV 和诊断信息。**扫描不等于清洗完毕**；请确认重复词、缺失词形、拆分字段和缺失批次。

### 3. 让 Agent 建立总纲

在 Claude/Claudian 中说：

```text
用 vocab-novel-studio 扫描 data/my-word-list.md，
建立 novels/my-novel/ 的总纲、词汇分配和进度台账。
先做数据核验与框架，不要写正文。
```

也可以把 `.claude/skills/vocab-novel-studio/prompts/01-framework-bootstrap.md` 一起交给模型。

确认人物、世界观、章节和词汇分配后，再开始正文。

### 4. 写一章

```text
用 vocab-novel-studio 继续写下一章。
```

或在有项目路径时：

```bash
python .claude/skills/vocab-novel-studio/scripts/novel.py \
  next --novel-dir novels/my-novel
```

### 5. 审计

```bash
python .claude/skills/vocab-novel-studio/scripts/novel.py \
  audit --novel-dir novels/my-novel \
  "novels/my-novel/chapters/第01章_标题.md"
```

退出码 `2` 表示存在缺失或 `INSET_ONLY` 目标词，应先修改章节再交付。

---

## 目录结构

```text
vocab-novel-studio/
├── .claude/
│   └── skills/
│       └── vocab-novel-studio/
│           ├── SKILL.md
│           ├── scripts/
│           │   ├── extract_words.py
│           │   └── novel.py
│           ├── prompts/
│           │   ├── 00-start-here.md
│           │   ├── 01-framework-bootstrap.md
│           │   ├── 02-write-chapter.md
│           │   ├── 03-audit-coverage.md
│           │   └── 04-custom-short-story.md
│           └── templates/
│               ├── 00_novel_bible.md
│               ├── 01_vocabulary_ledger.md
│               ├── 02_progress_ledger.md
│               ├── chapter_template.md
│               ├── short_story_template.md
│               ├── RESUME_CONTEXT.md
│               ├── CONTINUE_HERE.md
│               └── project_CLAUDE.md
├── tests/
│   └── smoke_test.py
├── .github/
│   └── workflows/
│       └── smoke.yml
├── README.md
├── LICENSE
└── .gitignore
```

---

## 设计原则

- **故事优先，词汇必须准确。**
- **计划覆盖 ≠ 正文覆盖。**
- **只有正文中的完整、自然实例才算覆盖。**
- **一个词第一次出现的地方就是它的记忆锚点；不要把它扔进章末表。**
- **不要把每个词机械配给一个角色或物件。**
- **不编造词源、搭配和覆盖率。**
- **人物要有独立目标；恋爱是关系的一种结果，不是奖励。**

详细的操作规范与触发条件在 `.claude/skills/vocab-novel-studio/SKILL.md`。五个独立 prompt 在同目录的 `prompts/`，可用于不支持 skills 的其他 Agent。

脚本命令在 skill 文件里使用 `<skill-dir>` 占位符：Claude Code 下是 `.claude/skills/vocab-novel-studio`，DSH 项目级安装下是 `.dsh/skills/vocab-novel-studio`。

---

## 已知限制

- `extract_words.py` 只负责解析，不会自动修复源数据的语义错误。
- `novel.py` 的覆盖审计只是词形初审；不规则词形、近义词、语义搭配仍需人工核验。
- 脚本默认接受中文项目路径与中文文件名；其他语言项目需要调整模板/命名。
- 不包含插图、排版引擎或 Anki 导出。
- `package_story.py` 需要本地文件系统和 Python；纯聊天 host 只能生成 Markdown，不能真正生成 zip。
- 新对话续写需要 `RESUME_CONTEXT.md`；没有它时，agent 不应假装记得上一段对话。

---

## 开发与测试

```bash
python tests/smoke_test.py
```

测试会创建一个临时词汇小说项目，验证：

- `novel.py next` 能找到下一章与目标词；
- 只出现在模拟阅读里的目标词被标记为 `INSET_ONLY`；
- 补进主线后覆盖通过；
- `extract_words.py` 能解析 Markdown 词表。

GitHub Actions 会在 push / pull request 时运行同一测试。

---

## 隐私与版权

- 本仓库刻意不包含任何真实小说正文、角色设定或原始词汇书数据。
- 使用他人的单词表前，请确认你有权使用/再分发。
- 如果要在公开仓库中包含自己的小说，请自行决定授权方式。
- 生成的章节和词表应由你自行检查与保管。

---

## License

MIT. See [LICENSE](LICENSE).

---

## English summary

Vocab Novel Studio is a reusable agent skill workflow for turning a user-supplied vocabulary list into a long-form novel or a customized short story with traceable word coverage. It includes data extraction, framework templates, an interview-first short-story mode, a chapter engine, a continuity/progress ledger, and a strict coverage auditor. Target words that appear only in inset texts (mock readings, exam passages, quotes) must also appear in the main plot to count. The repository intentionally ships without any copyrighted word list or novel text.
