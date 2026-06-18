# Agent reliability is a systems problem: checking claims against the work record

<div class="tool-callout" role="note" aria-label="Research Copilot announcement">
  <div class="tool-callout-text">
    <span class="tool-callout-label">New tool</span>
    This blog is created with the help of <strong>Research Copilot / PiPilot</strong> for Idea Brainstorm, Coding, Executing, Analyzing, and Writing. You can check the open-source tool
  </div>
  <div class="tool-callout-actions">
    <a class="primary" href="https://daidong.github.io/PiPilot/">Visit site</a>
    <a href="https://github.com/daidong/PiPilot">GitHub</a>
    <a href="post.html?slug=introducing-research-copilot">Read note</a>
  </div>
</div>

The [previous post](post.html?slug=black-box-llm-serving-caches) was about prompt caching. The main lesson was that a hidden serving system still exposes a contract to the application. If the provider reuses only serialized prefixes, then prompt order becomes a systems interface.

Agent systems have a similar contract, but the surface is different. A long-running agent does work and then reports what it did. It edits files, runs tests, cites papers, saves CSVs, makes plots, and writes a final summary. That summary is useful only when its claims match the work record.

The failure I worry about is not the answer that is obviously broken. It is the ordinary sentence that sounds complete but is not backed by the session: "all tests pass" after a later failing run, a paper citation that was never opened, a row count that the produced file does not have, or an output said to come from inputs the run never touched. These sentences look like normal progress reports, so they are easy to trust.

I built a small Claude Code plugin for this class of failure: [`provcheck-claude`](https://github.com/daidong/provcheck-claude). You run `/provcheck-claude:check`, and it asks a narrow question: did the agent's words match the evidence available when it spoke? The plugin is open source and runs on demand. There is no separate service and no extra API key. The deterministic checker runs locally; a small reviewer step runs through the user's normal Claude Code environment.

## Support is not correctness

The useful distinction is between correctness and support.

**Correctness** asks whether the result is true. Is the code right? Is the experiment meaningful? Does the figure support the claim? These questions usually need an oracle, a benchmark, or expert judgment.

**Support** asks a weaker question. Did the agent have evidence for the statement it made? If it said the CSV has 1.2M rows, can we inspect the actual file? If it said tests passed, did a test command pass after the relevant edit? If it cited a paper, did the session retrieve or read that paper before citing it?

A support check will not prove that the work is correct. It can still catch stale, missing, and mismatched evidence before a user trusts a result, commits code, or sends a report.

For this post I use three labels:

| Layer | Plain meaning | Example question |
| --- | --- | --- |
| L1 | What the agent told you | "The CSV has 5 columns." |
| L2 | What the trace recorded | Did a prior tool output say 5 columns? |
| L3 | What really exists or happened | Does the file on disk have 5 columns, and was it produced here? |

Most trajectory-checking work compares L1 with L2. It checks whether the agent's statement is supported by the recorded trajectory text. That is already valuable. TELBench/DRIFT, for example, gives 1,000 real deep-research trajectories with human-labeled error spans and a claim-centered method for checking whether earlier trajectory spans support later commitments.

The open space I care about is L1 against L3. If the agent claims a file has a property, the checker reads the real file. If the agent says a command produced an artifact, the checker looks at file changes and git state. At that point, agent reliability is no longer only a language problem. It is a systems problem.

## What the checker does

`provcheck-claude` is deliberately small. Install the plugin, run a Claude Code session, then type:

```text
/provcheck-claude:check
```

The plugin forks a reviewer subagent, so the main conversation only receives a compact report. The checker locates the session transcript, extracts checkable claims, compares them with evidence, and reports statements that are unsupported or contradicted. It never says that the whole session is correct.

The main design rule is that code handles hard evidence. The model helps extract claims that regexes miss and judges ambiguous cases, but it cannot invent a match that the transcript or file system does not contain.

The current checker looks for operational claims:

* tests, builds, and no-error statements;
* file edits, saved artifacts, and git actions;
* citations and source-use claims;
* searches and file-content assertions;
* counts and measurable file properties, such as rows, columns, and byte size;
* simple lineage statements, such as "output X came from input Y";
* environment, config, and schema claims when the evidence is visible.

It ignores plans, intentions, opinions, and semantic correctness claims. "The outputs match Table 2" is not a support claim. It asks whether a scientific comparison is true.

The second rule is time. A claim should be judged using evidence that existed before the claim. For ambiguous cases, the checker builds a small case bundle and gives the reviewer only the relevant earlier evidence. That keeps the report from crediting a statement with evidence found later.

The third piece is Tier-A capture. Two fail-open hooks record file metadata before and after file-touching tool calls: paths, sizes, mtimes, and created/modified/deleted sets. They do not copy file contents. This gives the checker enough L3 signal to say that a file was produced in the session and has not changed since capture before checking its rows or columns.

## What the external benchmark showed

TELBench is useful because it is external and human-labeled. It is not a direct plugin benchmark. Its trajectories are prose, not Claude Code's structured tool blocks, and the original files are not available. I used it as a mechanism test: can a support judge detect commitments that earlier trajectory evidence does not back?

Two results matter.

First, support checking has a ceiling. Sorting TELBench's 18 error types showed that a consistency checker can plausibly reach about 57% of the labeled errors. The other 43% are wrong-answer or semantic errors that require correctness judgment.

Second, the judge needs to be skeptical. A skeptical support prompt raised strict span recall from 58.1% to 71.3% on all 1,000 trajectories, while the share of flags landing on human-labeled error spans stayed around 72%. Counting partial support raised recall to 75.8%.

| TELBench operating point | Span recall | Any-gold precision |
| --- | ---: | ---: |
| Neutral support judge | 58.1% | — |
| Skeptical prompt, strict | **71.3%** | 71.9% |
| Skeptical prompt, counting partial support | 75.8% | about 72% |

This is a calibration result, not a product result. TELBench shows that claim-evidence consistency is a real signal and that prompt strictness matters. It does not validate the L1↔L3 part of the plugin, because TELBench has no artifact bytes to inspect.

## What the deployed-plugin benchmark showed

The second benchmark runs the shipped checker on self-contained Claude Code-style sessions. These sessions have real workspace files, transcripts, git state, and Tier-A capture diffs. Each case contains one judged claim labeled either `flag` or `clean`.

| Metric | Value |
| --- | ---: |
| Core flag cases | 17 |
| Surfaced recall, finding or reviewer bundle | **1.00** (17/17) |
| Recall decided by code alone | 0.71 (12/17) |
| Clean controls | 9 |
| Clean false-positive rate | **0.00** (0/9) |

By family, surfaced recall is 4/4 citation, 5/5 result, 5/5 artifact-property, 1/1 lineage, and 1/1 version-control. The seed benchmark is small and self-authored, so these numbers should not be read as a field-wide result. The useful point is that the benchmark runs the real matcher on real bytes.

It has already found two bugs.

The first was a build claim after a GNU Make failure. The transcript contained `make: *** [all] Error 1`, but the parser did not know that signature, so it treated the later build-success claim as supported. Adding the Make failure marker turned the case into a deterministic contradiction.

The second was missing-file handling. Flagging every absent file catches hallucinated outputs, but it also flags legitimate references to external inputs. The fix was to surface an absent file only when the session has positive evidence that the file was produced there: a captured command created it, or another claim said it was saved. That raised deterministic recall while keeping clean false positives at zero.

This is the engineering loop I want from an agent reliability tool: measure a concrete support failure, fix the matcher, rerun the benchmark, and keep the false-positive gate fixed.

## Why provenance alone is not enough

System provenance is the natural substrate for L3. AgentSight uses eBPF-style system observability for agents. PROV-AGENT extends W3C PROV concepts to agentic workflows. HPC workflow provenance systems can answer questions about what ran and what produced what.

Those records are useful, but capture is not checking. A provenance graph can say that a process opened files and wrote an output. It does not automatically compare the agent's natural-language claim against the produced bytes. It also does not prove semantic dataflow. If a process read `a.csv` and wrote `b.csv`, system access logs show possible ancestry. They do not show that bytes from `a.csv` determined `b.csv`.

That is why the current plugin starts with artifact state. Rows, columns, bytes, file existence, git state, and test outcomes are checkable against the real workspace. Full lineage is harder. More capture fidelity gives a better access graph, but not a proof that the agent's lineage sentence is true.

## What this does not do

The limits are real.

First, the checker tests support, not correctness. If a wrong conclusion is fully supported by bad evidence, this tool may not catch it.

Second, the L1↔L3 benchmark is only a seed. I wrote the cases, so a careful reader should discount the headline numbers. The next useful benchmark should come from tasks with independent answer keys: bug-fix tasks with hidden tests for stale "tests pass" claims, or data-analysis tasks with reference outputs for file-property claims.

Third, the capture layer is intentionally shallow. It records metadata, not contents. That is safer for everyday use, but it means some mismatches remain low confidence when the file may have changed after the claim.

These limits are the boundary of the tool, not incidental gaps.

## What this changes in agent-system design

Agent systems need reliability surfaces. A polished final answer is not enough. The system should know which claims are checkable, which evidence supports them, which claims are outside scope, and which claims were never checked.

A practical design checklist follows:

* Treat test/build claims as stateful. A passing run before later edits is not evidence that tests still pass.
* Treat citations as source-use claims. A citation should be tied to a retrieved or opened source, not just a plausible title.
* Treat produced files as inspectable artifacts. If the agent reports rows, columns, sizes, or schemas, read the file.
* Report coverage. A quiet checker should not imply that everything is verified.
* Keep hard checks in code. Use the model for extraction and ambiguous judgment, not for inventing evidence.
* Prefer artifact invariants over reconstructed lineage. File properties are often decidable; dataflow is often inferred.

The pattern from the prompt-cache post shows up again. The model is only one part of the system. The reliability contract comes from how model output, tool traces, files, git, and runtime evidence fit together.

## Try it

The plugin is open source: [`github.com/daidong/provcheck-claude`](https://github.com/daidong/provcheck-claude).

```bash
git clone https://github.com/daidong/provcheck-claude
claude --plugin-dir ./provcheck-claude
# inside a Claude Code session:
/provcheck-claude:check
```

You can also run the deterministic half directly on a transcript:

```bash
python3 scripts/provcheck_cli.py --session-id <session-id>
```

The current repository has 46 passing unit tests, a clean `ruff check .`, and a passing `claude plugin validate --strict .`. The deployed benchmark runs with:

```bash
python3 eval/score.py
```

I would use the checker after any long Claude Code session that ran tests, cited sources, produced data files, edited a repo, or wrote a final report that you are about to trust. It will not tell you the work is correct. It will tell you when some of the agent's claims do not match its own evidence.

---

# Agent 可靠性是一个系统问题：把它说的话对回工作记录

[上一篇](post.html?slug=black-box-llm-serving-caches)讲的是 prompt cache。那篇的核心教训是：一个隐藏在 provider 内部的 serving system，仍然会向应用暴露契约。如果 provider 只复用序列化前缀，prompt 顺序就变成了系统接口。

Agent 系统也有类似的契约，只是表面不同。一个长程 agent 做完事，会告诉你它做了什么。它改文件、跑测试、引用论文、保存 CSV、画图、写最终总结。这个总结只有在它的说法能对上工作记录时才有用。

我担心的失败，不是一眼就坏掉的答案，而是那些听起来很普通的完成句：后面已经有失败测试了，它还说 “all tests pass”；引用了一篇从没打开过的论文；报告了一个文件并没有的行数；或者说某个输出来自几个输入，但 trace 里看不出这些输入被用过。这些话看起来像正常进度汇报，所以很容易被相信。

我为这类失败做了一个 Claude Code 插件：[`provcheck-claude`](https://github.com/daidong/provcheck-claude)。你运行 `/provcheck-claude:check`，它问一个很窄的问题：agent 说这句话时，当时已有的证据撑不撑得起它？插件开源、按需运行，没有单独服务，也不需要额外 API key。确定性的 checker 在本地跑；少量 reviewer 判断走用户自己的 Claude Code 环境。

## 支撑不等于正确

这里有一个有用的区别：正确性和支撑性。

**正确性**问的是结果是不是真的。代码对不对？实验有没有意义？图能不能支撑结论？这些问题通常需要 oracle、benchmark，或者专家判断。

**支撑性**问的是更弱的问题。agent 说这句话时有没有证据？如果它说 CSV 有 120 万行，能不能读真实文件？如果它说测试通过了，相关改动之后有没有真的跑过并通过？如果它引用论文，session 里有没有先检索或读取这篇论文？

支撑性检查不会证明工作是正确的。但它可以在用户信任结果、提交代码、或发出报告之前，抓出 stale、missing 和 mismatched evidence。

这篇里我用三个标签：

| 层 | 白话意思 | 例子 |
| --- | --- | --- |
| L1 | agent 嘴上说了什么 | “CSV 有 5 列。” |
| L2 | trace 记录了什么 | 之前的工具输出有没有说 5 列？ |
| L3 | workspace 里真实存在或发生了什么 | 磁盘上的文件是否真的有 5 列，而且是不是本 session 产生的？ |

大多数 trajectory-checking 工作在对 L1 和 L2。它检查 agent 的说法能不能被记录下来的 trajectory 文本支撑。这已经很有价值。TELBench/DRIFT 就提供了 1000 条真实 deep-research trajectories 和人工标注的错误 spans，并用 claim-centered 方法检查前面的 trajectory spans 是否支撑后面的 commitments。

我更关心的空白是 L1 对 L3。agent 说一个文件有某个属性，checker 就读真实文件。agent 说某个命令生成了 artifact，checker 就看文件变化和 git state。到这里，agent 可靠性就不只是语言问题，而是系统问题。

## checker 做什么

`provcheck-claude` 故意做得很小。装好插件、跑完 Claude Code session 之后，输入：

```text
/provcheck-claude:check
```

插件会 fork 一个 reviewer subagent，所以主对话只收到一份简短报告。checker 会定位 session transcript，抽取可检查的 claims，对照 evidence，然后报告 unsupported 或 contradicted statements。它不会说整个 session 是正确的。

最主要的设计规则是：硬证据由代码处理。模型帮助抽取 regex 漏掉的 claims，也判断少数 ambiguous cases，但它不能凭空创造一个 transcript 或文件系统里不存在的 match。

当前 checker 检查的是很操作化的说法：

* 测试、build、no-error statements；
* 文件编辑、保存 artifact、git actions；
* 引用和 source-use claims；
* 搜索和文件内容断言；
* counts，以及 rows、columns、byte size 这类可测文件属性；
* 简单 lineage，比如 “output X came from input Y”；
* evidence 可见时的 environment、config 和 schema claims。

计划、意图、意见、以及语义正确性 claims 不在范围内。“outputs match Table 2” 不是支撑性 claim，它问的是一个科学比较是否真的成立。

第二条规则是时间。一个 claim 应该只用它之前已经存在的 evidence 来判断。对于 ambiguous cases，checker 会构建小的 case bundle，只给 reviewer 相关的早期 evidence。这样不会把 claim 之后才出现的证据偷偷算进去。

第三个组件是 Tier-A capture。两个 fail-open hooks 会在 file-touching tool calls 前后记录文件 metadata：paths、sizes、mtimes、created/modified/deleted sets。它不复制文件内容。这给 checker 足够的 L3 信号去判断：某个文件确实是本 session 产生的，并且 capture 之后没有变，然后再检查它的行数或列数。

## 外部 benchmark 说明了什么

TELBench 有用，因为它是外部数据，而且有人类标注。但它不是直接的插件 benchmark。它的 trajectories 是散文，不是 Claude Code 的结构化 tool blocks，原始文件也拿不到。所以我把它当成 mechanism test：一个 support judge 能不能发现前文证据撑不起的 commitments？

两个结果重要。

第一，支撑性检查有天花板。把 TELBench 的 18 种错误分类之后可以看到，一致性检查大概最多够到 57% 的标注错误。剩下 43% 是 wrong-answer 或 semantic errors，需要正确性判断。

第二，judge 必须更怀疑。一个 skeptical support prompt，把全部 1000 条 trajectories 上的 strict span recall 从 58.1% 提到 71.3%，同时 flags 落在人类标注错误上的比例仍然约 72%。如果把 partial support 也算进去，recall 到 75.8%。

| TELBench operating point | Span recall | Any-gold precision |
| --- | ---: | ---: |
| Neutral support judge | 58.1% | — |
| Skeptical prompt, strict | **71.3%** | 71.9% |
| Skeptical prompt, counting partial support | 75.8% | about 72% |

这是 calibration result，不是 product result。TELBench 说明 claim-evidence consistency 是真实信号，也说明 prompt strictness 很重要。但它没有验证插件最有差异化的 L1↔L3 部分，因为 TELBench 没有 artifact bytes 可以读。

## 部署版插件 benchmark 说明了什么

第二个 benchmark 直接跑 shipped checker，输入是自包含的 Claude Code 风格 sessions。这些 sessions 有真实 workspace files、transcripts、git state 和 Tier-A capture diffs。每个 case 只有一个被判断的 claim，标签是 `flag` 或 `clean`。

| Metric | Value |
| --- | ---: |
| Core flag cases | 17 |
| Surfaced recall, finding or reviewer bundle | **1.00** (17/17) |
| Recall decided by code alone | 0.71 (12/17) |
| Clean controls | 9 |
| Clean false-positive rate | **0.00** (0/9) |

按 family 分，surfaced recall 是 citation 4/4、result 5/5、artifact-property 5/5、lineage 1/1、version-control 1/1。这个 seed benchmark 很小，而且是我自己写的，所以不能把这些数字看成领域结论。它真正有用的地方是：它跑的是真 matcher，而且会读真实 bytes。

它已经找出了两个 bug。

第一个是 GNU Make failure 后的 build claim。transcript 里有 `make: *** [all] Error 1`，但 parser 不知道这个失败 signature，于是把后面的 build-success claim 当成 supported。加入 Make failure marker 之后，这个 case 变成了确定性的 contradiction。

第二个是 missing-file handling。把所有不存在的文件都标红，可以抓到幻觉输出，但也会误伤对外部输入文件的正常引用。修复办法是：只有当 session 有正证据表明这个文件是在这里产生的，才 surface absent file。例如 captured command 创建过它，或者另一个 claim 说保存过它。这样提高了 deterministic recall，同时把 clean false positives 保持在 0。

这正是我希望 agent reliability tool 具备的工程循环：测到一个具体 support failure，修 matcher，重跑 benchmark，同时守住 false-positive gate。

## 为什么 provenance 本身不够

系统 provenance 是 L3 的自然底座。AgentSight 用 eBPF 风格的系统观测来观察 agents。PROV-AGENT 把 W3C PROV 概念扩展到 agentic workflows。HPC workflow provenance 系统可以回答什么跑过、什么生成了什么。

这些记录有用，但 capture 不等于 checking。一个 provenance graph 可以说某个进程打开了哪些文件、写了哪个输出。它不会自动把 agent 的自然语言 claim 对回产物 bytes。它也不能证明语义 dataflow。如果一个进程读了 `a.csv`、写了 `b.csv`，系统访问日志说明的是可能的 ancestry，不是 `a.csv` 的 bytes 真的决定了 `b.csv`。

所以当前插件先关注 artifact state。rows、columns、bytes、file existence、git state、test outcomes 都可以对真实 workspace 检查。完整 lineage 更难。更强的 capture fidelity 会给出更完整的 access graph，但不会自动证明 agent 的 lineage 句子是真的。

## 它不做什么

这些限制是真实边界。

第一，它检查支撑性，不检查正确性。如果一个错误结论被坏证据完整支撑，这个工具可能抓不到。

第二，L1↔L3 benchmark 只是 seed。我自己写了 cases，所以读者应该 discount 这些数字。下一步更有用的 benchmark 应该来自带独立 answer keys 的任务：例如 bug-fix tasks 用 hidden tests 自动标 stale “tests pass” claims，或者 data-analysis tasks 用 reference outputs 标文件属性 claims。

第三，当前 capture 层有意很浅。它记录 metadata，不记录 contents。这对日常使用更安全，但也意味着如果文件可能在 claim 之后变过，一些 mismatch 只能保持 low confidence。

这些限制是工具边界，不是顺手补一下就能消失的小缺口。

## 这对 agent 系统设计有什么影响

Agent 系统需要显式的 reliability surfaces。一个漂亮的 final answer 不够。系统应该知道哪些 claims 可检查，哪些 evidence 支撑它们，哪些 claims 超出范围，哪些 claims 根本没检查过。

一个实用 checklist 是：

* 把 test/build claims 当成有状态的东西。后续改动之前的 passing run，不等于现在 tests still pass。
* 把 citations 当成 source-use claims。citation 应该能连到 retrieved 或 opened source，而不是只看起来像一篇合理的论文。
* 把 produced files 当成可检查 artifacts。agent 报 rows、columns、sizes、schemas，就读文件。
* 报告 coverage。checker 没说话，不等于所有东西都 verified。
* 硬检查留给代码。模型用于 extraction 和 ambiguous judgment，不用于发明 evidence。
* 优先检查 artifact invariants，而不是重建完整 lineage。文件属性经常可判；dataflow 经常只是推断。

prompt-cache 那篇里的模式在这里又出现了一次。模型只是系统的一部分。可靠性契约来自 model output、tool traces、files、git 和 runtime evidence 怎么接在一起。

## 试用

插件开源：[`github.com/daidong/provcheck-claude`](https://github.com/daidong/provcheck-claude)。

```bash
git clone https://github.com/daidong/provcheck-claude
claude --plugin-dir ./provcheck-claude
# 在 Claude Code session 里：
/provcheck-claude:check
```

也可以直接对 transcript 跑确定性部分：

```bash
python3 scripts/provcheck_cli.py --session-id <session-id>
```

当前仓库有 46 个 passing unit tests，`ruff check .` clean，`claude plugin validate --strict .` 通过。部署版 benchmark 这样跑：

```bash
python3 eval/score.py
```

我会在任何长 Claude Code session 之后使用它，尤其是 session 跑了测试、引用了来源、产出了数据文件、改了 repo、或者写了一份你准备信任的 final report。它不会告诉你工作是正确的。它会告诉你，agent 的某些话有没有对上它自己的证据。
