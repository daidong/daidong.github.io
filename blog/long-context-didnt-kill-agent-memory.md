# Agent Memory: Accuracy, Cost, and Gaps.

<div class="tool-callout" role="note" aria-label="Research Copilot announcement">
  <div class="tool-callout-text">
    <span class="tool-callout-label">New tool</span>
    This blog was created with help from <strong>Research Copilot / PiPilot</strong> for brainstorming, coding, execution, analysis, and writing. You can check out the open-source tool here:
  </div>
  <div class="tool-callout-actions">
    <a class="primary" href="https://daidong.github.io/PiPilot/">Visit site</a>
    <a href="https://github.com/daidong/PiPilot">GitHub</a>
    <a href="post.html?slug=introducing-research-copilot">Read note</a>
  </div>
</div>

Frontier LLMs now advertise million-token context windows. So what is agent memory still for?

My current answer is narrower than I expected: **the part that clearly works today is cost**. A memory layer can make a long-running agent cheaper and faster at similar accuracy. The bigger promises, remembering beyond the window, learning from a changing history, and resolving contradictions over time, are still open. They are real problems. Current systems have not proved that they solve them.

The gap is not just a weak-method problem. It is also a measurement problem. We do not yet have the benchmark that would tell us whether an agent has memory in the strong sense, rather than a cheaper retrieval path over old text.

## The old accuracy argument is mostly gone

For a while, the standard argument for agent memory was simple: a memory system should answer long-history questions more accurately than a full-context baseline. Full context means putting the whole history into the prompt and asking the model to read it directly.

That argument has weakened because many memory benchmarks are now short enough to fit inside modern context windows. When the whole history fits, reading everything is hard to beat.

On **LoCoMo**, the Mem0 paper reports that a full-context method reading roughly 26,000 tokens still gets the highest J score, the paper's LLM-as-a-judge metric, at about 73% ([Mem0, arXiv:2504.19413](https://arxiv.org/abs/2504.19413)). The strongest retrieval baseline is around 61%, Mem0 itself is around 67%, and Mem0's graph variant is around 68.4%. In that setting, memory does not win the accuracy race. It wins elsewhere.

On **DMR**, the older benchmark used by MemGPT, the result is even cleaner. Zep's paper reports that a plain full-conversation baseline reaches 94.4% with GPT-4 Turbo and 98.0% with GPT-4o-mini, because each conversation has only about 60 messages and fits easily in current context windows ([Zep, arXiv:2501.13956](https://arxiv.org/abs/2501.13956)). At that point, the benchmark is close to saturated. A memory system can match or slightly beat it, but the test no longer separates memory from prompt stuffing.

So yes, long context did kill one version of the memory story. If the claim is "memory is more accurate than full context on short-history QA," that claim is no longer a strong reason to build a memory system.

## The part that survived is cost

Memory survives for a narrower and more practical reason: **it can reduce per-query cost**.

A full-context agent pays to re-read the whole history on every turn. A memory system pays once to ingest, store, and organize the history, then answers later queries from a smaller retrieved context. That trade only pays off when the same history will be queried many times, but that is exactly the common long-running-agent setting.

The measurements have the same shape across papers. In LoCoMo, full context pays the latency of reading about 26k tokens per query, with a reported total p95 latency, meaning 95th-percentile latency, around 17 seconds. Mem0 answers from a much smaller memory representation with p95 latency around 1.44 seconds and more than 90% token-cost savings relative to full context ([Mem0, arXiv:2504.19413](https://arxiv.org/abs/2504.19413)). In **LongMemEval S**, where histories are around 115k tokens, Zep reports 15.2% and 18.5% accuracy improvements over full-context baselines with GPT-4o-mini and GPT-4o, while reducing response latency by about 90% ([Zep, arXiv:2501.13956](https://arxiv.org/abs/2501.13956)).

A million-token window does not make it cheap to put a million tokens into every prompt. It raises the amount you can include. The bill still grows with attention work, key-value (KV) cache memory, and time to first token. Memory is the system-level move that changes the cost curve.

That is the honest product claim: memory trades write-time work for cheaper repeated reads. The number to report is not accuracy alone. It is dollars and p95 latency at a fixed accuracy.

## The stronger promises are still gaps

The deeper promise of memory is not cost. It is that an agent can keep useful state across time and revise that state when the world changes.

The first part is **persistence beyond the window**. The evidence for this problem is real. NoLiMa shows that effective context can be much shorter than advertised context: GPT-4o drops from 99.3% on short inputs to 69.7% at 32k tokens, and 11 of 13 models claiming 128k or more fall below half of their own short-context score by 32k ([NoLiMa, arXiv:2502.05167](https://arxiv.org/abs/2502.05167)). RULER makes the same broad point: many models that advertise long contexts do not maintain strong performance at the lengths they claim ([RULER, arXiv:2404.06654](https://arxiv.org/abs/2404.06654)).

LongMemEval adds a second point. Even when the answer fits inside the window, a model can read the full history worse than it reads the right slice. On the roughly 115k-token LongMemEval S setting, GPT-4o gets 87.0% in an oracle setting that receives only the evidence sessions, but 60.6% when reading the full history without the paper's Chain-of-Note reading prompt, a prompt that asks the model to take notes over retrieved evidence before answering ([LongMemEval, arXiv:2410.10813](https://arxiv.org/abs/2410.10813)). The problem is not only capacity. It is reading.

But these results do not yet prove persistence beyond modern windows. A 115k-token history already fits inside many frontier models. Re-running these studies with a real 1M-window model such as [DeepSeek-V4-Pro](https://api-docs.deepseek.com/news/news260424) would likely raise the full-context baseline. It still would not answer the harder question: what happens when the history does not fit at all?

The second part is **learning from a changing history**. Real user histories contradict themselves. A user moves, changes jobs, revises a preference, or corrects a fact. A useful memory system should not return both the old fact and the new fact with equal confidence. It should update, version, reconcile, or ask.

Long context does not do that. It re-reads. Current memory systems mostly do not do it either. MemoryAgentBench is useful here because it tests memory agents on accurate retrieval, test-time learning, long-range understanding, and selective forgetting. Its results are blunt: on multi-hop selective forgetting, all methods reach at most 7% accuracy, and the paper argues that current memory systems still behave like agentic retrieval-augmented generation (RAG), meaning they fetch partial past context and answer from it rather than form a coherent updated state ([MemoryAgentBench, arXiv:2507.05257](https://arxiv.org/abs/2507.05257)).

This is the part that retrieval alone cannot solve. A search over raw logs can return "user lives in New York" and "user lives in Boston" together. Something still has to decide which fact is current, whether the old fact should remain as history, and whether the conflict should be surfaced to the user.

The obvious fix is to let the model rewrite its own memory: consolidate old entries into corrected ones instead of piling them up. But that step is itself fragile. Zhang et al. have an LLM continuously consolidate past trajectories into a textual memory bank, and find a consistent inverted-U: utility rises early, then degrades, and can fall below the no-memory baseline as updates accumulate. The cleanest case is stark. Even when consolidating from ground-truth solutions, GPT-5.4 fails on 54% of ARC-AGI problems it had already solved without any memory ([Faulty Memories, arXiv:2605.12978](https://arxiv.org/abs/2605.12978)). Each consolidation pass is a lossy rewrite: useful details get dropped, spurious rules get added. Their robust default is the opposite of a clean self-rewriting store. Keep the raw episodes, because an episodic-only control that simply retains trajectories stays competitive with the consolidators they test.

The frontier response is to move consolidation offline, like sleep. Auto-Dreamer splits fast per-session writing from a slow consolidator that rewrites memory into a compact, abstracted set, reporting 41.1% on ScienceWorld, 7 points over the strongest baseline with 12x less memory ([Auto-Dreamer, arXiv:2605.20616](https://arxiv.org/abs/2605.20616)). That direction is promising, but the previous paragraph is the warning: the same consolidation that helps offline is what corrupts memory when it runs carelessly online.

The real design space has at least three ways to read the past: retrieval, which is cheap and returns slices; long context, which sees more but is expensive and degrades with length; and parametric memory, which writes information into model weights and is still mostly a research direction. The hard problem, reconciling a changing history, sits above all three.

## The missing benchmark is more specific than "long"

The field already has very long benchmarks. BABILong scatters reasoning facts through natural text, provides splits up to 10 million tokens, and reports recurrent-memory experiments up to 50 million tokens. Its headline result is that models effectively use only 10-20% of the context ([BABILong, arXiv:2406.10149](https://arxiv.org/abs/2406.10149)).

But length alone is not the missing piece. The benchmark we need combines four properties:

| Benchmark family | Very long? | Conversational or agentic? | Updates and contradictions? | Main gap |
| --- | :---: | :---: | :---: | --- |
| BABILong, RULER, NoLiMa | yes | no | no | Mostly synthetic long-context reading. |
| LoCoMo, LongMemEval S | partly | yes | limited | Often still fits in current long windows. |
| MemoryAgentBench | yes | simulated multi-turn | yes | Gets closest, but is still not a natural months-long mixed-use agent trace. |
| **What strong memory needs** | **yes, beyond the window** | **yes** | **yes** | Topic drift, stale facts, updates, and tool-using work records in one trace. |

This is why "memory beats long context" remains too easy to argue and too hard to settle. A benchmark that fits in the window mostly tests reading. A benchmark with contradictions but synthetic chunks tests update logic, but not the messy history of a real assistant. A benchmark with million-token documents tests length, but not conversational change.

The useful benchmark would look more like months of real agent use: project work, casual preferences, code edits, document analysis, abandoned plans, corrections, and topic shifts. Some facts should expire. Some should remain true only in a time range. Some should conflict. The answer key should reward updating and forgetting, not just recall.

And the problem is not only the dataset. It is the metric. Flynt notes that every major memory benchmark, LoCoMo foremost, scores whether the model answered correctly, not whether the memory system retrieved correctly. A system that returns its entire store gets recall 1.0 and passes answer-quality evaluation. Measured in isolation, memory baselines reach mean retrieval precision of just 0.05 to 0.08, even on questions about their own extractions ([PrecisionMemBench, arXiv:2605.11325](https://arxiv.org/abs/2605.11325)). We are often grading the reader, not the memory.

## What this means for builders

If you build agent systems today, the clean framing is narrower than the marketing language.

* Sell memory on cost and latency at fixed accuracy. That is the part with strong evidence.

* Treat persistence beyond the context window as an open capability until the evaluation history actually exceeds the model's effective window.

* Treat memory writes carefully. Storing every extracted sentence forever is a retrieval index, not a memory, but letting the model endlessly rewrite its own store corrupts it (the inverted-U above). The safer default today is to keep raw episodes and consolidate sparingly and with gates, not on every update.

* Report what the system does when facts conflict: overwrite, version, keep both, ask the user, or mark uncertainty.

* Do not hide the read-time/write-time trade. Memory saves repeated reads by spending effort during ingestion and consolidation.

A bigger context window changes the break-even point. It does not remove the systems problem. A useful long-running agent is defined by what it keeps, what it spends, and what it does when its own records disagree. Today, only the spending part is well measured. That is both the limitation and the opening.

---

前沿 LLM 已经开始宣传百万 token 的 context window。那 agent memory 还剩什么用？

我现在的答案比预想窄：**今天能明确交付的，是成本。** Memory layer 可以让一个长程 agent 在相近准确率下更便宜、更快。更大的那些承诺，记住窗口之外、从变化的历史中学习、处理随时间出现的矛盾，仍然是开放问题。它们是真问题，但现有系统还没有证明自己解决了它们。

这个缺口不只是方法不够强。它也是一个测量问题。我们还没有那个 benchmark，能告诉我们一个 agent 是否真的有强意义上的记忆，而不只是对旧文本做了更便宜的检索。

## 旧的准确率论证基本结束了

过去一段时间，agent memory 的标准论证很简单：memory 系统应该比 full-context baseline 更准确。Full context 指把整段历史直接塞进 prompt，让模型自己读。

这套论证变弱了，因为很多 memory benchmark 的历史已经短到能放进现代 context window。只要整段历史放得下，直接全读就很难被打败。

在 **LoCoMo** 上，Mem0 论文报告说，直接读约 26,000 token 的 full-context 方法仍然拿到最高 J score，也就是论文里的 LLM-as-a-judge 指标，约 73%（[Mem0, arXiv:2504.19413](https://arxiv.org/abs/2504.19413)）。最强的 retrieval baseline 约 61%，Mem0 自己约 67%，Mem0 的 graph variant 约 68.4%。在这个设定里，memory 没有赢准确率这场比赛。它赢在别的地方。

在 **DMR** 上，结论更干净。DMR 是 MemGPT 用过的早期 memory benchmark。Zep 论文报告，一个普通的 full-conversation baseline 在 GPT-4 Turbo 上达到 94.4%，在 GPT-4o-mini 上达到 98.0%，因为每段 conversation 只有约 60 条消息，轻松放进当前 context window（[Zep, arXiv:2501.13956](https://arxiv.org/abs/2501.13956)）。到这个程度，benchmark 基本饱和。Memory 系统可以追平或略高一点，但这个测试已经很难区分 memory 和 prompt stuffing。

所以，是的，长上下文确实杀死了一种 memory 故事。如果论点是“memory 在短历史 QA 上比 full context 更准”，那已经不是一个强理由了。

## 活下来的部分是成本

Memory 活下来的理由更窄，也更实际：**它能降低每次 query 的成本。**

Full-context agent 每一轮都要重新读整段历史。Memory 系统先花一次成本摄取、存储、组织历史，然后后续 query 只读更小的 retrieved context。这笔账只有在同一段历史会被反复查询时才划算，而这正是长程 agent 的常见场景。

不同论文里的测量形状很一致。在 LoCoMo 上，full context 每次 query 都要读约 26k token，报告的 total p95 latency 约 17 秒；p95 指 95th-percentile latency，也就是最慢 5% 请求边界附近的延迟。Mem0 用更小的 memory representation 作答，p95 latency 约 1.44 秒，相比 full context 节省超过 90% token cost（[Mem0, arXiv:2504.19413](https://arxiv.org/abs/2504.19413)）。在 **LongMemEval S** 上，历史约 115k token。Zep 报告说，在 GPT-4o-mini 和 GPT-4o 上，它相对 full-context baseline 分别提升 15.2% 和 18.5% accuracy，同时把 response latency 降低约 90%（[Zep, arXiv:2501.13956](https://arxiv.org/abs/2501.13956)）。

百万 token 窗口不会让“每轮塞一百万 token”变便宜。它只是提高了你能塞进去的上限。账单仍然会随着 attention 计算、key-value (KV) cache 内存、首 token 延迟一起涨。Memory 是系统层面改变成本曲线的办法。

所以，诚实的产品论点应该是：memory 用写入时的工作，换更便宜的重复读取。该报告的数字不是准确率本身，而是在固定准确率下的美元成本和 p95 latency。

## 更强的承诺仍然没被证明

Memory 更深的承诺不是成本，而是 agent 能跨时间保留有用状态，并在世界变化时修改这个状态。

第一部分是**窗口之外的持久性**。问题本身有证据支持。NoLiMa 表明，有效 context 可能远短于宣传 context：GPT-4o 从短输入的 99.3% 掉到 32k token 处的 69.7%；13 个声称支持 128k 以上的模型里，有 11 个在 32k 处掉到自身短上下文成绩的一半以下（[NoLiMa, arXiv:2502.05167](https://arxiv.org/abs/2502.05167)）。RULER 也给出同样的整体结论：很多宣传长上下文的模型，在自己声称的长度上并不能保持强性能（[RULER, arXiv:2404.06654](https://arxiv.org/abs/2404.06654)）。

LongMemEval 又补了一点。即使答案在窗口内，模型读完整历史，也可能不如只读正确切片。在约 115k token 的 LongMemEval S 设定中，GPT-4o 在只拿到 evidence sessions 的 oracle setting 下得到 87.0%，但在不使用论文里的 Chain-of-Note reading prompt 时只有 60.6%；这个 prompt 会要求模型先对检索到的 evidence 做笔记，再回答问题（[LongMemEval, arXiv:2410.10813](https://arxiv.org/abs/2410.10813)）。问题不只是装不下，也是读不好。

但这些结果还不能证明窗口之外的持久性。115k token 的历史已经能放进很多前沿模型。即使用一个真实 1M window 的模型，比如 [DeepSeek-V4-Pro](https://api-docs.deepseek.com/news/news260424)，重跑这些研究，full-context baseline 很可能会上升。它仍然回答不了更难的问题：当历史根本放不下时会怎样？

第二部分是**从变化的历史中学习**。真实用户历史会自相矛盾。用户会搬家、换工作、改变偏好，或者纠正以前说过的事实。一个有用的 memory 系统不应该把旧事实和新事实以同等置信度一起返回。它应该更新、版本化、消解矛盾，或者反问。

长上下文不做这件事。它只是重读。当前 memory 系统大多也没有做好。MemoryAgentBench 在这里有价值，因为它测试 memory agent 的 accurate retrieval、test-time learning、long-range understanding 和 selective forgetting。它的结果很直接：在 multi-hop selective forgetting 上，所有方法最高只有 7% accuracy；论文也指出，当前 memory 系统仍然像 agentic retrieval-augmented generation (RAG)，也就是检索部分过去上下文再回答，而不是形成一个一致的更新后状态（[MemoryAgentBench, arXiv:2507.05257](https://arxiv.org/abs/2507.05257)）。

这正是单纯 retrieval 解决不了的部分。对原始日志做搜索，可能会同时返回“用户住在 New York”和“用户住在 Boston”。仍然需要有东西决定哪个事实现在有效，旧事实是否要作为历史保留，以及是否应该把冲突告诉用户。

显而易见的修法，是让模型重写自己的记忆：把旧条目 consolidate 成更正后的条目，而不是一直往上堆。但这一步本身就很脆弱。Zhang 等人让一个 LLM 持续把过去的 trajectory consolidate 进一个文本 memory bank，发现一条稳定的倒 U 曲线：utility 先上升，然后随着更新累积而退化，甚至掉到 no-memory baseline 以下。最干净的案例很刺眼。即便是从 ground-truth 解答做 consolidation，GPT-5.4 在那些它本来不靠记忆就已经解出的 ARC-AGI 题目上，仍有 54% 做错（[Faulty Memories, arXiv:2605.12978](https://arxiv.org/abs/2605.12978)）。每一次 consolidation 都是一次有损重写：有用的细节被丢掉，虚假的规则被塞进来。他们给出的稳健默认做法，恰好和“自我重写的干净存储”相反。保留原始 episode，因为一个只保留 trajectory 的 episodic-only 对照组，和他们测试的各种 consolidator 相比依然有竞争力。

前沿的回应，是把 consolidation 挪到离线，像睡眠一样。Auto-Dreamer 把快速的单 session 写入和慢速的 consolidator 拆开，让后者把记忆重写成一份紧凑、抽象的集合，报告在 ScienceWorld 上达到 41.1%，比最强 baseline 高 7 个点，而内存少用 12 倍（[Auto-Dreamer, arXiv:2605.20616](https://arxiv.org/abs/2605.20616)）。这个方向有希望，但上一段就是警告：同一个在离线时有帮助的 consolidation，一旦在线上随意运行，就是腐蚀记忆的那一步。

真正的设计空间至少有三种读过去的方式：retrieval，便宜、只取切片；long context，看得更多，但贵，而且长度一长就退化；parametric memory，把信息写进模型权重，目前仍主要是研究方向。最难的问题，如何消解一段会变化的历史，横跨这三条路线。

## 缺的 benchmark 不只是“长”

这个领域已经有很长的 benchmark。BABILong 把推理事实撒进自然文本，提供到 1000 万 token 的切片，并报告了 recurrent-memory 方法到 5000 万 token 的实验。它的核心结论是，模型实际上只有效使用了 10-20% 的 context（[BABILong, arXiv:2406.10149](https://arxiv.org/abs/2406.10149)）。

但长度本身不是缺口。我们真正需要的 benchmark 要同时有四个性质：

| Benchmark family | 很长？ | 对话或 agent 形态？ | 有更新和矛盾？ | 主要缺口 |
| --- | :---: | :---: | :---: | --- |
| BABILong, RULER, NoLiMa | 是 | 否 | 否 | 主要是合成长上下文阅读。 |
| LoCoMo, LongMemEval S | 部分 | 是 | 有限 | 通常仍放得进当前长窗口。 |
| MemoryAgentBench | 是 | 模拟多轮 | 是 | 最接近，但还不是自然的、跨数月的混合用途 agent trace。 |
| **强 memory 真正需要的** | **是，超过窗口** | **是** | **是** | 在同一条 trace 里有 topic drift、过时事实、更新和工具使用记录。 |

这就是为什么“memory 打败 long context”仍然很容易争论，却很难定论。一个放得进窗口的 benchmark，主要测试阅读能力。一个有矛盾但由合成 chunk 构造的 benchmark，可以测试更新逻辑，但不像真实助手的混乱历史。一个百万 token 文档 benchmark 测长度，却不测对话中的变化。

真正有用的 benchmark 应该更像几个月的真实 agent 使用：项目工作、日常偏好、代码修改、文档分析、废弃计划、纠错、topic 切换。有些事实应该过期。有些事实只在某段时间内为真。有些事实应该冲突。答案集应该奖励更新和遗忘，而不只是奖励召回。

而且问题不只在数据集，还在指标。Flynt 指出，几乎所有主流 memory benchmark（首先就是 LoCoMo）衡量的是模型有没有答对，而不是 memory 系统有没有检索对。一个把整个 store 全部返回的系统，recall 是 1.0，照样能通过答案质量评估。单独测量检索时，memory baseline 的平均检索 precision 只有 0.05 到 0.08，即便问的就是它自己抽取出来的内容（[PrecisionMemBench, arXiv:2605.11325](https://arxiv.org/abs/2605.11325)）。我们常常是在给“读者”打分，而不是给“记忆”打分。

## 对 builder 的含义

如果你今天在做 agent 系统，最清楚的 framing 比市场语言要窄。

* 用固定准确率下的 cost 和 latency 来卖 memory。这是证据最强的部分。

* 在 evaluation history 真正超过模型有效窗口之前，把窗口之外的持久性当成开放能力，而不是已完成特性。

* 谨慎对待 memory write。把每个抽取出来的句子永远存下来，是 retrieval index，不是 memory；但让模型无止境地重写自己的存储，会把它腐蚀掉（上文那条倒 U 曲线）。今天更稳妥的默认做法，是保留原始 episode，并且有节制、带门控地做 consolidation，而不是每次更新都重写。

* 报告系统遇到事实冲突时怎么做：覆盖、版本化、两个都留、反问用户，还是标记不确定。

* 不要隐藏 read-time/write-time trade。Memory 用摄取和 consolidation 的成本，换更便宜的重复读取。

更大的 context window 会改变 break-even point。它不会移除这个系统问题。一个有用的长程 agent，取决于它保留什么、花费什么，以及当自己的记录互相冲突时怎么处理。今天，只有花费这一项被比较好地测量了。这既是限制，也是机会。
