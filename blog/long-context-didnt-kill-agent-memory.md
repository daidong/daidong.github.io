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

Frontier LLMs now advertise million-token context windows. If a model can read the whole history anyway, what is a separate memory system still for?

My answer came out narrower than I expected. The part that clearly pays off today is **cost**: a memory layer makes a long-running agent cheaper and faster at about the same accuracy. The larger promises, remembering past the window, learning from a history that keeps changing, reconciling facts that contradict each other, are still open. They are real problems, and no current system has shown it solves them.

That gap is half a methods problem and half a measurement problem. We still have no benchmark that can tell whether an agent has memory in the strong sense, or just a cheaper way to re-read old text.

## First, what a memory system actually does

"Memory" gets attached to everything from a vector database to fine-tuning, so it helps to pin down the narrow version this post is about. A memory system gives an agent state that outlives the context window, with explicit operations to write things down, organize them, pull the right piece back, and drop what has gone stale. That is more than retrieval over a fixed corpus (RAG), and more than a longer window. The defining move is that the agent's own experience, what it saw, what it concluded, what it got wrong, becomes durable, queryable state.

A useful way to break that down, borrowed from the memory literature, is six operations: **write** (decide what to keep), **consolidate** (turn raw records into stable knowledge), **index** (organize it so it can be found), **retrieve** (choose what to pull back), **read** (actually fold it into the model's working context), and **forget** (drop what is wrong or stale). Almost every system you have heard of is one specific set of choices over these six. CoALA, the paper most of this vocabulary comes from, makes the sharp observation that a memory read or write is itself an action the agent chooses to take ([CoALA, arXiv:2309.02427](https://arxiv.org/abs/2309.02427)). That is what makes the memory *agentic* rather than a fixed pipeline.

The most useful thing you notice with that list is where the engineering effort has gone. Systems pour work into **index** and **retrieve**, the search half, and very little into **consolidate** and **forget**. Yet consolidate-and-forget is the half that separates a memory from a search engine. A good index finds the right old sentence. Only a memory decides that the old sentence is now wrong and should be replaced.

Two traditions sit under most designs. One copies human memory: keep a running stream of everything that happened, score each entry by how recent, important, and relevant it is, and periodically stop to reflect, folding the raw log into higher-level notes. That is the Generative Agents line ([arXiv:2304.03442](https://arxiv.org/abs/2304.03442)). The other copies operating systems: treat the context window as fast memory (RAM) and external storage as slow memory (disk), and page between them, with "memory pressure" warnings when the window fills. That is MemGPT ([arXiv:2310.08560](https://arxiv.org/abs/2310.08560)). The OS analogy has been pushed a long way: newer systems raise a "page fault" when the model asks for something it already evicted, and pin the hot items it keeps reaching for. Real products mix the two, but the poles are a good way to read any new system.

## The old accuracy argument is mostly gone

For a while the case for memory was simple: a memory system should answer long-history questions more accurately than a full-context baseline, where full context means dumping the whole history into the prompt and letting the model read it directly.

That case weakened as the popular memory benchmarks turned out to fit inside modern context windows. When the whole history fits, reading all of it is hard to beat.

On **LoCoMo**, the Mem0 paper reports that a full-context method reading about 26,000 tokens still gets the highest J score, the paper's LLM-as-a-judge metric, at roughly 73% ([Mem0, arXiv:2504.19413](https://arxiv.org/abs/2504.19413)). The strongest retrieval baseline sits around 61%, Mem0 itself around 67%, and its graph variant around 68.4%. Memory does not win the accuracy race here; its advantage shows up elsewhere.

On **DMR**, the older benchmark from MemGPT, the picture is simpler still. Zep reports that a plain full-conversation baseline reaches 94.4% with GPT-4 Turbo and 98.0% with GPT-4o-mini, because each conversation runs only about 60 messages and fits easily in today's windows ([Zep, arXiv:2501.13956](https://arxiv.org/abs/2501.13956)). At that point the benchmark is saturated: a memory system can match it or edge ahead, but the test no longer tells memory apart from prompt stuffing.

So long context did kill one version of the memory story. "Memory is more accurate than full context on short-history QA" is no longer a strong reason to build one.

## What survived is cost

Memory survives for a narrower, more practical reason: it lowers the cost of each query.

A full-context agent pays to re-read the entire history on every turn. A memory system pays once to ingest and organize the history, then answers later queries from a much smaller retrieved slice. That trade only pays off when the same history is queried many times, which is exactly the long-running-agent setting.

The measurements line up across papers. On LoCoMo, full context reads about 26k tokens per query, with a reported p95 latency, the 95th-percentile slow-tail boundary, around 17 seconds. Mem0 answers from a smaller memory representation at about 1.44 seconds p95 and over 90% lower token cost ([Mem0, arXiv:2504.19413](https://arxiv.org/abs/2504.19413)). On **LongMemEval S**, where histories run around 115k tokens, Zep reports 15.2% and 18.5% accuracy gains over full-context baselines with GPT-4o-mini and GPT-4o, while cutting response latency by about 90% ([Zep, arXiv:2501.13956](https://arxiv.org/abs/2501.13956)).

A million-token window does not make it cheap to put a million tokens in every prompt. It raises the ceiling on what you can include. The bill still climbs with attention work, key-value (KV) cache memory, and time to first token. Memory is the systems-level move that bends the cost curve.

So the honest pitch for memory is this: it trades write-time work for cheaper repeated reads. The number to put on the slide is dollars and p95 latency at a fixed accuracy, not accuracy on its own.

## The stronger promises are still gaps

Memory's deeper promise is not cost. It is that an agent can hold useful state across time and revise that state when the world changes.

The first part is **persistence past the window**. The evidence that this is a real problem is strong. NoLiMa shows that effective context can be far shorter than the advertised number: GPT-4o falls from 99.3% on short inputs to 69.7% at 32k tokens, and 11 of 13 models claiming 128k or more drop below half their own short-context score by 32k ([NoLiMa, arXiv:2502.05167](https://arxiv.org/abs/2502.05167)). RULER makes the same point broadly: many models that advertise long context do not hold up at the lengths they claim ([RULER, arXiv:2404.06654](https://arxiv.org/abs/2404.06654)).

LongMemEval adds a second, less obvious point: even when the answer sits inside the window, a model can read the full history worse than it reads the right slice. On the roughly 115k-token LongMemEval S setting, GPT-4o gets 87.0% when handed only the evidence sessions (an oracle), but 60.6% reading the full history without the paper's Chain-of-Note prompt, which asks the model to take notes on retrieved evidence before answering ([LongMemEval, arXiv:2410.10813](https://arxiv.org/abs/2410.10813)). The same paper finds commercial assistants degrade hard on long histories: ChatGPT and Coze on GPT-4o drop 37% and 64% against their oracle-retrieval scores. So the bottleneck is not only capacity; it is how the model reads. How you read the history matters about as much as what you retrieve.

But none of this yet proves persistence past *modern* windows. A 115k-token history already fits inside many frontier models. Re-running these studies on a true 1M-window model such as [DeepSeek-V4-Pro](https://api-docs.deepseek.com/news/news260424) would likely lift the full-context baseline. It still would not answer the harder question: what happens when the history does not fit at all?

The second part is **learning from a history that changes**. Real user histories contradict themselves. People move, switch jobs, change a preference, correct an earlier fact. A useful memory system should not hand back the old fact and the new fact with equal confidence; it should update, version, reconcile, or ask.

Long context does none of that; it just re-reads. Most current memory systems do not do it either. MemoryAgentBench is helpful here because it tests memory agents on accurate retrieval, test-time learning, long-range understanding, and selective forgetting. The numbers are low where it counts: on multi-hop selective forgetting, every method tops out around 7% accuracy, and the authors argue that today's systems still behave like agentic retrieval-augmented generation (RAG). They fetch some past context and answer from it, rather than maintain a single updated state ([MemoryAgentBench, arXiv:2507.05257](https://arxiv.org/abs/2507.05257)).

This is the part plain retrieval cannot fix. A search over raw logs can return "user lives in New York" and "user lives in Boston" side by side. Something still has to decide which one holds now, whether the old one stays as history, and whether the conflict should be raised with the user.

The obvious fix is to let the model rewrite its own memory, folding old entries into corrected ones instead of stacking them up. But that step is fragile. Zhang et al. have an LLM continuously consolidate past trajectories into a text memory bank, and find a consistent inverted-U: usefulness climbs early, then degrades as updates pile up, and can fall below a no-memory baseline. One result stands out. Even when consolidating from ground-truth solutions, GPT-5.4 fails 54% of ARC-AGI problems it had already solved with no memory at all ([Faulty Memories, arXiv:2605.12978](https://arxiv.org/abs/2605.12978)). Each consolidation pass is a lossy rewrite: useful detail drops out, spurious rules creep in. Their safe default runs the other way: keep the raw episodes, because a control that only retains trajectories stays competitive with the consolidators they test.

The frontier response is to move consolidation offline, like sleep. Auto-Dreamer splits fast per-session writing from a slow consolidator that rewrites memory into a compact, abstracted set, reporting 41.1% on ScienceWorld, 7 points over the strongest baseline with 12x less memory ([Auto-Dreamer, arXiv:2605.20616](https://arxiv.org/abs/2605.20616)). Promising, but the previous paragraph is the warning: the same consolidation that helps offline is what corrupts memory when it runs carelessly online.

There is also a kind of memory this whole discussion has quietly skipped. Everything above is about remembering *facts*. Agents also need to remember *how to do things*, what the field calls procedural memory, or skills. Voyager is the clean demonstration: an agent playing Minecraft writes each behavior it gets working as a small piece of code into a growing skill library, then retrieves and reuses it later instead of re-deriving it ([Voyager, arXiv:2305.16291](https://arxiv.org/abs/2305.16291)). This is the same gap from another angle. On MemoryAgentBench, test-time learning, building up reusable competence from experience, is exactly where current systems score lowest. Storing facts is the part we can do; turning experience into skill is the part we mostly cannot.

The design space has at least three ways to read the past: retrieval, cheap and slice-by-slice; long context, which sees more but costs more and frays with length; and parametric memory, which writes information into the model weights and is still mostly a research direction. The hard problem, reconciling a history that changes, sits above all three.

## Where the field is pushing, 2025 into 2026

The gaps above are exactly what the most recent work is aimed at. Four directions are worth watching, and together they sketch where agent memory is heading.

**Consolidation is moving offline, on a sleep analogy.** The fragile step from the last section, rewriting memory while a task runs, gets safer if you move it out of the hot path. The framing borrows from how brains are thought to consolidate during sleep: write fast during the day, replay and reorganize slowly offline. Sleep-time Compute makes the agent "think" about a stored context before any query arrives, and reports +13% on a stateful version of GSM-Symbolic and +18% on stateful AIME from spending that idle compute ([Sleep-time Compute, arXiv:2504.13171](https://arxiv.org/abs/2504.13171)). Auto-Dreamer, from the last section, applies the same split to memory itself: fast per-session writes, a slow background consolidator that rewrites the store into a compact form ([Auto-Dreamer, arXiv:2605.20616](https://arxiv.org/abs/2605.20616)). A more aggressive version pushes consolidation all the way into the weights through an offline distillation phase ([Language Models Need Sleep, arXiv:2606.03979](https://arxiv.org/abs/2606.03979)). The bet across all three is that the expensive, error-prone work of reorganizing memory should not happen mid-conversation.

**The write is becoming a decision you can audit, not a side effect.** Most systems write greedily: extract a fact, store it. The 2026 work treats what enters memory as a budgeted choice with its own quality bar. CraniMem gates writes with a goal-conditioned score, admitting only items that are relevant to the current goal, important, or surprising into a bounded buffer, and reports that this holds up better than both storing everything and compressing aggressively when the input is full of distractors ([CraniMem, arXiv:2603.15642](https://arxiv.org/abs/2603.15642)). MEMAUDIT goes after the thing answer-accuracy hides: it scores the write itself, including whether a system lays down "tombstones" (explicit deletion markers) when a fact is invalidated, and finds missed invalidations and absent tombstones in the exported stores of Mem0, A-MEM, and Letta ([MEMAUDIT, arXiv:2605.02199](https://arxiv.org/abs/2605.02199)). A store that never marks anything as deleted looks fine on a QA score and is quietly broken.

**Compressing the agent's own context is now its own subfield, and the dumb baseline is hard to beat.** Long-running agents drown in their own tool outputs, so a 2025–2026 line treats the running transcript as working memory to fold in place. AgentFold lets the agent emit a "fold" directive each step and keeps its context near 7k tokens after 100 turns, where a plain ReAct log would sit around 91k ([AgentFold, arXiv:2510.24699](https://arxiv.org/abs/2510.24699)). ReSum and ACON instead learn the compressor, training a policy to summarize the history at the right boundaries ([ReSum, arXiv:2509.13313](https://arxiv.org/abs/2509.13313); [ACON, arXiv:2510.00615](https://arxiv.org/abs/2510.00615)). But the most useful result is a cautionary one: on software-engineering agents, simply masking old tool outputs beyond a window matches or beats a trained LLM summarizer on both cost and solve rate, and the summaries can make trajectories up to 15% longer ([The Complexity Trap, arXiv:2508.21433](https://arxiv.org/abs/2508.21433)). What you drop matters more than how cleverly you compress what is left. AGORA pushes that logic further, scoring which observation-action steps to keep with a 125M model trained on whether removing a step would have changed the next action, at about 2ms per step and no per-step LLM call ([AGORA, arXiv:2605.26596](https://arxiv.org/abs/2605.26596)).

**The policy itself is starting to be learned, not scripted.** Most deployed memory is a hand-written pipeline: these rules decide what to store, that ranker decides what to fetch. A newer line trains the memory agent end to end against the task it serves ([Learning to Remember, arXiv:2602.18493](https://arxiv.org/abs/2602.18493); [MemTrain, arXiv:2606.03197](https://arxiv.org/abs/2606.03197)), and the latent-memory branch attaches a small learned memory module to a frozen model, such as a gated bank that adds under 3% parameters ([G-MemLLM, arXiv:2602.00015](https://arxiv.org/abs/2602.00015)). A related result on the retrieval side: once memory is split across several stores, choosing which store to query matters more than ranking within one. An oracle router reaches higher accuracy with 62% fewer context tokens than querying every store, and the gap widens as histories grow, because pulling everything from a large episodic store actively hurts ([Cost-Sensitive Store Routing, arXiv:2603.15658](https://arxiv.org/abs/2603.15658)).

Step back and the through-line is a shift in where agent capability is thought to live: out of the weights, past the prompt, and into an external runtime of memory, skills, and protocols that the agent operates ([Externalization in LLM Agents, arXiv:2604.08224](https://arxiv.org/abs/2604.08224)). That is the optimistic read. The sober one is that almost every result above is a 2025–2026 preprint reporting its own numbers, and the field still has no shared test that says which of these moves actually produces memory rather than a faster cache. That is the gap the next section is about.

## The missing benchmark is more specific than "long"

The field already has very long benchmarks. BABILong scatters reasoning facts through natural text, offers splits up to 10 million tokens, and reports recurrent-memory runs to 50 million. Its headline finding is that models effectively use only 10-20% of the context they are given ([BABILong, arXiv:2406.10149](https://arxiv.org/abs/2406.10149)).

But length alone is not the missing piece. The benchmark we need has four properties at once:

| Benchmark family             |         Very long?         | Conversational or agentic? | Updates and contradictions? | Main gap                                                                     |
| ---------------------------- | :------------------------: | :------------------------: | :-------------------------: | ---------------------------------------------------------------------------- |
| BABILong, RULER, NoLiMa      |             yes            |             no             |              no             | Mostly synthetic long-context reading.                                       |
| LoCoMo, LongMemEval S        |           partly           |             yes            |           limited           | Often still fits in current long windows.                                    |
| MemoryAgentBench             |             yes            |    simulated multi-turn    |             yes             | Gets closest, but is still not a natural months-long mixed-use agent trace.  |
| **What strong memory needs** | **yes, beyond the window** |           **yes**          |           **yes**           | Topic drift, stale facts, updates, and tool-using work records in one trace. |

That is why "memory beats long context" stays easy to argue and hard to settle. A benchmark that fits in the window mostly tests reading. A benchmark with contradictions but synthetic chunks tests update logic, but not the messy history of a real assistant. A benchmark with million-token documents tests length, but not conversational change.

The benchmark we actually want would look like months of real agent use: project work, casual preferences, code edits, document analysis, abandoned plans, corrections, and topic shifts. Some facts should expire. Some should be true only inside a date range. Some should conflict. The answer key should reward updating and forgetting, not just recall.

And the dataset is only half of it; the metric is the other half. Flynt notes that nearly every major memory benchmark, LoCoMo first among them, scores whether the model answered correctly, not whether the memory system retrieved correctly. A system that returns its whole store gets recall 1.0 and sails through answer-quality scoring. Measured on its own, retrieval precision for these memory baselines runs just 0.05 to 0.08, even on questions about their own extractions ([PrecisionMemBench, arXiv:2605.11325](https://arxiv.org/abs/2605.11325)). We are often grading the reader, not the memory.

## What this means for builders

If you build agent systems today, the honest framing is narrower than the marketing.

* Sell memory on cost and latency at a fixed accuracy. That is the part with strong evidence behind it.

* Treat persistence past the context window as an open capability until your evaluation history actually exceeds the model's effective window, which, per NoLiMa, is shorter than the spec sheet.

* Handle memory writes with care. Storing every extracted sentence forever gives you a retrieval index, not a memory; letting the model endlessly rewrite its own store corrupts it (the inverted-U above). The safer default today is to keep raw episodes and consolidate sparingly, behind gates, not on every update.

* Before reaching for a clever summarizer, try the dumb baseline. On long agent trajectories, simply hiding old tool outputs beyond a window often matches or beats a trained LLM summarizer on cost and success rate, and weak summaries can make a run longer rather than shorter. What you drop matters more than how you compress what is left.

* Remember that memory is more than facts. If your agent solves the same class of task repeatedly, the higher-value memory is procedural: save the working procedure, not just the transcript.

* Say what your system does when facts conflict: overwrite, version, keep both, ask the user, or flag uncertainty.

* Do not hide the read-time/write-time trade. Memory buys cheaper repeated reads by spending effort during ingestion and consolidation.

A bigger context window moves the break-even point. It does not remove the systems problem. A useful long-running agent is defined by what it keeps, what it spends, and what it does when its own records disagree. Today only the spending is well measured. That is both the limit and the opening.

---

前沿 LLM 已经开始宣传百万 token 的 context window。如果模型反正能把整段历史读一遍，那一个单独的 memory 系统还剩什么用？

我的答案比预想窄。今天能明确交付的，是**成本**：memory layer 可以让一个长程 agent 在相近准确率下更便宜、更快。更大的那些承诺，记住窗口之外、从不断变化的历史中学习、消解互相矛盾的事实，仍然是开放问题。它们是真问题，但还没有哪个现有系统证明自己解决了它们。

这个缺口一半是方法问题，一半是测量问题。我们还没有那个 benchmark，能告诉我们一个 agent 是否真的有强意义上的记忆，还是只有一条更便宜的重读旧文本的路。

## 先说清楚：一个 memory 系统到底在做什么

记忆这个词，从向量数据库到微调都能套上，所以先把这篇文章说的那个窄义版本钉清楚。一个 memory 系统给 agent 一份能活过 context window 的状态，并带有明确的操作：把东西写下来、组织起来、在需要时取回正确的那一块、丢掉过时的部分。这比在固定语料上做检索（RAG）更宽，也比单纯加长窗口更宽。真正的定义性动作是：agent 自己的经历，它看到什么、得出什么结论、在哪里出错，变成持久、可查询的状态。

把这件事拆开的一个好用方式（借自 memory 文献）是六个操作：**write**（决定保留什么）、**consolidate**（把原始记录变成稳定的知识）、**index**（组织起来以便找到）、**retrieve**（挑出要取回的部分）、**read**（真正把它折叠进模型当前的工作上下文）、**forget**（丢掉错的或过时的）。你听说过的几乎每个系统，都是在这六个操作上做的一组具体选择。这套词汇大多来自 CoALA，它有一个很准的观察：一次 memory 的读或写，本身就是 agent 选择去做的一个 action（[CoALA, arXiv:2309.02427](https://arxiv.org/abs/2309.02427)）。这正是 memory 之所以"agentic"、而不是一条固定流水线的原因。

拿着这张清单，最值得注意的是工程力气花在了哪里。系统在 **index** 和 **retrieve**，也就是搜索这一半，上投入很多，而在 **consolidate** 和 **forget** 上几乎没有投入。但 consolidate 和 forget 恰恰是把 memory 和搜索引擎区分开的那一半。一个好的 index 能找到那句正确的旧话；只有 memory 能判断那句旧话现在已经错了，应该被替换。

大多数设计底下有两条传统。一条照搬人类记忆：保留一条记录一切的 stream，按每条的 recency、importance、relevance 打分，并周期性地停下来 reflect，把原始日志折叠成更高层的笔记。这是 Generative Agents 这一脉（[arXiv:2304.03442](https://arxiv.org/abs/2304.03442)）。另一条照搬操作系统：把 context window 当成快速内存（RAM），把外部存储当成慢速内存（disk），在两者之间 page，窗口快满时还会发出"memory pressure"警告。这是 MemGPT（[arXiv:2310.08560](https://arxiv.org/abs/2310.08560)）。这个 OS 类比被推得很远：更新的系统会在模型请求一个已经被换出的东西时触发"page fault"，并把它反复要的热条目 pin 住。真实产品会把两条混着用，但这两个极点是读懂任何新系统的好办法。

## 旧的准确率论证基本结束了

过去一段时间，agent memory 的标准论证很简单：memory 系统应该比 full-context baseline 更准确。Full context 指把整段历史直接塞进 prompt，让模型自己读。

这套论证变弱了，因为很多 memory benchmark 的历史已经短到能放进现代 context window。只要整段历史放得下，直接全读就很难被打败。

在 **LoCoMo** 上，Mem0 论文报告说，直接读约 26,000 token 的 full-context 方法仍然拿到最高 J score，也就是论文里的 LLM-as-a-judge 指标，约 73%（[Mem0, arXiv:2504.19413](https://arxiv.org/abs/2504.19413)）。最强的 retrieval baseline 约 61%，Mem0 自己约 67%，Mem0 的 graph variant 约 68.4%。在这里 memory 没赢准确率，它的优势在别的地方。

在 **DMR** 上，画面更简单。DMR 是 MemGPT 用过的早期 memory benchmark。Zep 论文报告，一个普通的 full-conversation baseline 在 GPT-4 Turbo 上达到 94.4%，在 GPT-4o-mini 上达到 98.0%，因为每段 conversation 只有约 60 条消息，轻松放进当前 context window（[Zep, arXiv:2501.13956](https://arxiv.org/abs/2501.13956)）。到这个程度，benchmark 已经饱和：memory 系统可以追平或略高一点，但这个测试已经分不出 memory 和 prompt stuffing。

所以，长上下文确实杀死了一种 memory 故事。如果论点是"memory 在短历史 QA 上比 full context 更准"，那已经不是一个强理由了。

## 活下来的是成本

Memory 活下来的理由更窄，也更实际：它能降低每次 query 的成本。

Full-context agent 每一轮都要重新读整段历史。Memory 系统先花一次成本摄取、组织历史，然后后续 query 只读更小的 retrieved 切片。这笔账只有在同一段历史会被反复查询时才划算，而这正是长程 agent 的常见场景。

不同论文里的测量很一致。在 LoCoMo 上，full context 每次 query 都要读约 26k token，报告的 p95 latency，也就是 95th-percentile、最慢那一档的边界，约 17 秒。Mem0 用更小的 memory representation 作答，p95 latency 约 1.44 秒，token 成本降低超过 90%（[Mem0, arXiv:2504.19413](https://arxiv.org/abs/2504.19413)）。在 **LongMemEval S** 上，历史约 115k token，Zep 报告说，在 GPT-4o-mini 和 GPT-4o 上，它相对 full-context baseline 分别提升 15.2% 和 18.5% accuracy，同时把 response latency 降低约 90%（[Zep, arXiv:2501.13956](https://arxiv.org/abs/2501.13956)）。

百万 token 窗口不会让"每轮塞一百万 token"变便宜。它只是提高了你能塞进去的上限。账单仍然会随着 attention 计算、key-value (KV) cache 内存、首 token 延迟一起涨。Memory 是在系统层面把成本曲线掰弯的办法。

所以，关于 memory 的诚实说法是：它用写入时的工作，换更便宜的重复读取。该写在 slide 上的数字，是固定准确率下的美元成本和 p95 latency，而不是准确率本身。

## 更强的承诺仍然没被证明

Memory 更深的承诺不是成本，而是 agent 能跨时间保留有用状态，并在世界变化时修改这个状态。

第一部分是**窗口之外的持久性**。问题本身有充分证据。NoLiMa 表明，有效 context 可能远短于宣传 context：GPT-4o 从短输入的 99.3% 掉到 32k token 处的 69.7%；13 个声称支持 128k 以上的模型里，有 11 个在 32k 处掉到自身短上下文成绩的一半以下（[NoLiMa, arXiv:2502.05167](https://arxiv.org/abs/2502.05167)）。RULER 给出同样的整体结论：很多宣传长上下文的模型，在自己声称的长度上并不能保持。

LongMemEval 又补了一个不那么显然的点：即使答案在窗口内，模型读完整历史，也可能不如只读正确切片。在约 115k token 的 LongMemEval S 设定中，GPT-4o 在只拿到 evidence sessions 的 oracle setting 下得到 87.0%，但在不使用论文里的 Chain-of-Note prompt 时只有 60.6%；这个 prompt 会要求模型先对检索到的 evidence 做笔记，再回答（[LongMemEval, arXiv:2410.10813](https://arxiv.org/abs/2410.10813)）。同一篇论文还发现，商用助手在长历史上掉得很厉害：ChatGPT 和 Coze 在 GPT-4o 上相对各自的 oracle 检索分数分别掉了 37% 和 64%。所以瓶颈不只是装不下，还在于怎么读。你怎么读这段历史，和你检索到什么几乎一样重要。

但这些结果还不能证明*现代*窗口之外的持久性。115k token 的历史已经能放进很多前沿模型。即使用一个真实 1M window 的模型，比如 [DeepSeek-V4-Pro](https://api-docs.deepseek.com/news/news260424)，重跑这些研究，full-context baseline 很可能会上升。它仍然回答不了更难的问题：当历史根本放不下时会怎样？

第二部分是**从变化的历史中学习**。真实用户历史会自相矛盾。用户会搬家、换工作、改变偏好，或者纠正以前说过的事实。一个有用的 memory 系统不应该把旧事实和新事实以同等置信度一起返回；它应该更新、版本化、消解矛盾，或者反问。

长上下文不做这件事，它只是重读。当前 memory 系统大多也没做。MemoryAgentBench 在这里有用，因为它测试 memory agent 的 accurate retrieval、test-time learning、long-range understanding 和 selective forgetting。最关键的地方数字很低：在 multi-hop selective forgetting 上，所有方法最高只有约 7% accuracy；论文也指出，当前系统仍然像 agentic retrieval-augmented generation (RAG)，检索部分过去上下文再回答，而不是维护一个统一的更新后状态（[MemoryAgentBench, arXiv:2507.05257](https://arxiv.org/abs/2507.05257)）。

这正是单纯 retrieval 解决不了的部分。对原始日志做搜索，可能会同时返回"用户住在 New York"和"用户住在 Boston"。仍然需要有东西决定哪个现在有效，旧的是否要作为历史保留，以及是否应该把冲突告诉用户。

显而易见的修法，是让模型重写自己的记忆：把旧条目折叠成更正后的条目，而不是一直往上堆。但这一步很脆弱。Zhang 等人让一个 LLM 持续把过去的 trajectory consolidate 进一个文本 memory bank，发现一条稳定的倒 U 曲线：utility 先上升，然后随着更新累积而退化，甚至掉到 no-memory baseline 以下。有一个结果很扎眼。即便是从 ground-truth 解答做 consolidation，GPT-5.4 在那些它本来不靠记忆就已经解出的 ARC-AGI 题目上，仍有 54% 做错（[Faulty Memories, arXiv:2605.12978](https://arxiv.org/abs/2605.12978)）。每一次 consolidation 都是一次有损重写：有用的细节被丢掉，虚假的规则被塞进来。他们的稳妥默认做法正好相反：保留原始 episode，因为一个只保留 trajectory 的对照组，和他们测试的各种 consolidator 相比依然有竞争力。

前沿的回应，是把 consolidation 挪到离线，像睡眠一样。Auto-Dreamer 把快速的单 session 写入和慢速的 consolidator 拆开，让后者把记忆重写成一份紧凑、抽象的集合，报告在 ScienceWorld 上达到 41.1%，比最强 baseline 高 7 个点，而内存少用 12 倍（[Auto-Dreamer, arXiv:2605.20616](https://arxiv.org/abs/2605.20616)）。有希望，但上一段就是警告：同一个在离线时有帮助的 consolidation，一旦在线上随意运行，就是腐蚀记忆的那一步。

还有一种 memory，被上面整段讨论悄悄跳过了。前面说的全是记住*事实*。Agent 还需要记住*怎么做事*，也就是 procedural memory，或者说技能。Voyager 是干净的例子：一个在 Minecraft 里玩的 agent，把每个调通的行为写成一小段代码，存进不断增长的 skill library，之后直接取回复用，而不是重新推导一遍（[Voyager, arXiv:2305.16291](https://arxiv.org/abs/2305.16291)）。这其实是同一个缺口的另一面：在 MemoryAgentBench 上，test-time learning，从经验里攒出可复用的能力，正是当前系统得分最低的地方。存事实是我们能做的部分；把经验变成技能，是我们大多还做不到的部分。

真正的设计空间至少有三种读过去的方式：retrieval，便宜、只取切片；long context，看得更多，但更贵，而且长度一长就退化；parametric memory，把信息写进模型权重，目前仍主要是研究方向。最难的问题，如何消解一段会变化的历史，横跨这三条路线。

## 这个领域在往哪推：2025 年底到 2026 年

上面那些缺口，正是最近的工作主攻的方向。有四条值得盯着，合起来能勾出 agent memory 大致要去哪里。

**Consolidation 正在挪到离线，用的是"睡眠"这个类比。** 上一节那个脆弱的步骤——在任务进行中重写记忆——一旦挪出主路径就会更安全。这个想法借自大脑被认为在睡眠时做 consolidation 的方式：白天快速写入，离线时慢慢 replay、重组。Sleep-time Compute 让 agent 在任何 query 到来之前，先对一段存好的 context "想一想"，并报告这笔空闲算力带来 +13%（stateful 版 GSM-Symbolic）和 +18%（stateful AIME）的提升（[Sleep-time Compute, arXiv:2504.13171](https://arxiv.org/abs/2504.13171)）。上一节的 Auto-Dreamer 把同样的拆分用在记忆本身：快速的单 session 写入，加一个慢速后台 consolidator 把存储重写成紧凑形式（[Auto-Dreamer, arXiv:2605.20616](https://arxiv.org/abs/2605.20616)）。更激进的一种，干脆通过一个离线蒸馏阶段，把 consolidation 一路推进到权重里（[Language Models Need Sleep, arXiv:2606.03979](https://arxiv.org/abs/2606.03979)）。三者共同的赌注是：重组记忆这种又贵又容易出错的活，不该在对话进行中做。

**Write 正在变成一个可以审计的决定，而不是顺手的副作用。** 大多数系统是贪婪地写：抽出一个事实，就存下。2026 年的工作把"什么进入记忆"当成一个有预算的选择，并给它自己的质量标准。CraniMem 用一个 goal-conditioned 的分数给写入把关，只让与当前目标相关、重要或令人意外的条目进入一个有界 buffer，并报告说在输入充满干扰项时，这比"全存"和"激进压缩"都更扛得住（[CraniMem, arXiv:2603.15642](https://arxiv.org/abs/2603.15642)）。MEMAUDIT 则盯住答案准确率掩盖掉的东西：它给写入本身打分，包括系统在一个事实被推翻时有没有放下"tombstone"（明确的删除标记），并在 Mem0、A-MEM、Letta 导出的存储里发现了漏掉的失效和缺失的 tombstone（[MEMAUDIT, arXiv:2605.02199](https://arxiv.org/abs/2605.02199)）。一个从不标记删除的存储，在 QA 分数上看着没事，实际上已经悄悄坏了。

**压缩 agent 自己的 context 已经成了一个独立的小领域，而且那个"笨"baseline 很难打。** 长程 agent 会被自己的 tool 输出淹没，所以 2025–2026 有一条线把运行中的 transcript 当作工作记忆就地折叠。AgentFold 让 agent 每一步发出一个"fold"指令，在 100 轮之后把 context 维持在约 7k token，而一个普通 ReAct 日志大概会停在 91k 左右（[AgentFold, arXiv:2510.24699](https://arxiv.org/abs/2510.24699)）。ReSum 和 ACON 则改为把压缩器学出来，训练一个策略在合适的边界上对历史做摘要（[ReSum, arXiv:2509.13313](https://arxiv.org/abs/2509.13313)；[ACON, arXiv:2510.00615](https://arxiv.org/abs/2510.00615)）。但最有用的是那个反例：在软件工程 agent 上，简单地把窗口之外的旧 tool 输出 mask 掉，在成本和解决率上追平甚至打败训练过的 LLM summarizer，而那些摘要还能把轨迹拉长最多 15%（[The Complexity Trap, arXiv:2508.21433](https://arxiv.org/abs/2508.21433)）。丢掉什么，比多聪明地压缩剩下的更重要。AGORA 把这个逻辑再往前推，用一个 125M 的模型给"该保留哪些 observation-action 步"打分，训练信号是"删掉这一步会不会改变下一个动作"，每步约 2ms，且没有逐步的 LLM 调用（[AGORA, arXiv:2605.26596](https://arxiv.org/abs/2605.26596)）。

**策略本身也开始是学出来的，而不是写死的。** 大多数已部署的 memory 是一条手写流水线：这套规则决定存什么，那个 ranker 决定取什么。更新的一条线把 memory agent 针对它服务的任务端到端训练（[Learning to Remember, arXiv:2602.18493](https://arxiv.org/abs/2602.18493)；[MemTrain, arXiv:2606.03197](https://arxiv.org/abs/2606.03197)），而 latent-memory 这一支则给冻结的模型挂上一个小的可学习记忆模块，比如一个只增加不到 3% 参数的 gated bank（[G-MemLLM, arXiv:2602.00015](https://arxiv.org/abs/2602.00015)）。检索一侧有个相关结果：一旦 memory 被拆到多个 store，决定查哪个 store 比在一个 store 内部排序更重要。一个 oracle router 用比"全查一遍"少 62% 的 context token 拿到更高准确率，而且历史越长差距越大，因为从一个很大的 episodic store 里全捞出来反而有害（[Cost-Sensitive Store Routing, arXiv:2603.15658](https://arxiv.org/abs/2603.15658)）。

退一步看，这条主线其实是 agent 能力被认为存放在哪里的一次转移：从权重里出来，越过 prompt，进入一个由 agent 操作的、由 memory、skills 和 protocol 组成的外部运行时（[Externalization in LLM Agents, arXiv:2604.08224](https://arxiv.org/abs/2604.08224)）。这是乐观的读法。清醒的读法是：上面几乎每一个结果都是 2025–2026 的 preprint 在报告自己的数字，而这个领域仍然没有一个共享的测试，能说清这些动作里哪一个真正产出了记忆，而不只是一个更快的 cache。这正是下一节要谈的缺口。

## 缺的 benchmark 不只是"长"

这个领域已经有很长的 benchmark。BABILong 把推理事实撒进自然文本，提供到 1000 万 token 的切片，并报告了 recurrent-memory 方法到 5000 万 token 的实验。它的核心结论是，模型实际上只有效使用了 10-20% 的 context（[BABILong, arXiv:2406.10149](https://arxiv.org/abs/2406.10149)）。

但长度本身不是缺口。我们真正需要的 benchmark 要同时有四个性质：

| Benchmark family        |     很长？    | 对话或 agent 形态？ | 有更新和矛盾？ | 主要缺口                                      |
| ----------------------- | :--------: | :-----------: | :-----: | ----------------------------------------- |
| BABILong, RULER, NoLiMa |      是     |       否       |    否    | 主要是合成长上下文阅读。                              |
| LoCoMo, LongMemEval S   |     部分     |       是       |    有限   | 通常仍放得进当前长窗口。                              |
| MemoryAgentBench        |      是     |      模拟多轮     |    是    | 最接近，但还不是自然的、跨数月的混合用途 agent trace。         |
| **强 memory 真正需要的**      | **是，超过窗口** |     **是**     |  **是**  | 在同一条 trace 里有 topic drift、过时事实、更新和工具使用记录。 |

这就是为什么"memory 打败 long context"仍然很容易争论，却很难定论。一个放得进窗口的 benchmark，主要测试阅读能力。一个有矛盾但由合成 chunk 构造的 benchmark，可以测试更新逻辑，但不像真实助手的混乱历史。一个百万 token 文档 benchmark 测长度，却不测对话中的变化。

真正有用的 benchmark 应该更像几个月的真实 agent 使用：项目工作、日常偏好、代码修改、文档分析、废弃计划、纠错、topic 切换。有些事实应该过期。有些事实只在某段时间内为真。有些事实应该冲突。答案集应该奖励更新和遗忘，而不只是奖励召回。

而且数据集只是一半，指标是另一半。Flynt 指出，几乎所有主流 memory benchmark（首先就是 LoCoMo）衡量的是模型有没有答对，而不是 memory 系统有没有检索对。一个把整个 store 全部返回的系统，recall 是 1.0，照样能通过答案质量评估。单独测量检索时，这些 memory baseline 的平均检索 precision 只有 0.05 到 0.08，即便问的就是它自己抽取出来的内容（[PrecisionMemBench, arXiv:2605.11325](https://arxiv.org/abs/2605.11325)）。我们常常是在给"读者"打分，而不是给"记忆"打分。

## 对 builder 的含义

如果你今天在做 agent 系统，诚实的 framing 比市场语言要窄。

* 用固定准确率下的 cost 和 latency 来卖 memory。这是证据最强的部分。

* 在 evaluation history 真正超过模型有效窗口之前，把窗口之外的持久性当成开放能力，而不是已完成特性；而按 NoLiMa，这个有效窗口比 spec sheet 上写的要短。

* 谨慎对待 memory write。把每个抽取出来的句子永远存下来，得到的是 retrieval index，不是 memory；但让模型无止境地重写自己的存储，会把它腐蚀掉（上文那条倒 U 曲线）。今天更稳妥的默认做法，是保留原始 episode，并且有节制、带门控地做 consolidation，而不是每次更新都重写。

* 在掏出花哨的 summarizer 之前，先试试最笨的 baseline。在长 agent 轨迹上，简单地把窗口之外的旧 tool 输出藏起来，在成本和成功率上往往能追平甚至打败训练过的 LLM summarizer；而差的摘要会让一次运行更长，而不是更短。丢掉什么，比怎么压缩剩下的更重要。

* 记住 memory 不只是事实。如果你的 agent 反复解同一类任务，更高价值的 memory 是 procedural 的：存下那套能跑通的流程，而不只是对话记录。

* 报告系统遇到事实冲突时怎么做：覆盖、版本化、两个都留、反问用户，还是标记不确定。

* 不要隐藏 read-time/write-time trade。Memory 用摄取和 consolidation 的成本，换更便宜的重复读取。

更大的 context window 会挪动 break-even point。它不会移除这个系统问题。一个有用的长程 agent，取决于它保留什么、花费什么，以及当自己的记录互相冲突时怎么处理。今天，只有花费这一项被比较好地测量了。这既是限制，也是机会。
