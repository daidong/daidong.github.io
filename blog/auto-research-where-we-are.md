# Auto Research Is Real. It's Just Not What People Think.

Over the past few months, I've spent most of my time building and using autonomous research agents: systems that search the literature, write code, run experiments, and draft papers with surprisingly little human help. I've read a lot of the recent work in this area, and I've also spent enough API money to learn, firsthand, **where the demos end and the real problems begin**. BTW, two systems we built: **[Research Copilot](https://daidong.github.io/post.html?slug=introducing-research-copilot)** and **[Research Assistant Mode](https://daidong.github.io/post.html?slug=introducing-ram-desktop)**

The short version is simple. Auto research is real, and it is getting better fast. But it is not replacing researchers. It is changing where human effort matters.

---

## Workflow-capable, execution-fragile

That can be hard to see because the surface now looks so polished. Systems like **[The AI Scientist](https://arxiv.org/abs/2408.06292)**, **[Agent Laboratory](https://arxiv.org/abs/2501.04227)**, and **[EvoScientist](https://arxiv.org/abs/2603.08127)** have shown that LLM-based agents can move through the whole outer shape of a research project: read papers, propose ideas, write code, run experiments, analyze results, and draft a manuscript. If you judge by the workflow diagram alone, the future can look almost settled.

In practice, though, moving through the steps of research is not the same thing as doing reliable science.

The phrase that still feels most accurate to me is **workflow-capable, execution-fragile**. These systems can often produce paper-shaped output. Much less reliably, they produce science you would want to trust. A nice figure may come from a broken pipeline. A polished summary may miss the one paper that ruins the whole premise. A result section can sound perfectly confident while resting on an experiment that never actually ran.

I don't think this is some rare failure mode. It seems closer to the default way these systems go wrong when the task rewards plausible narration more than grounded execution.

The recent benchmarks point in the same direction. **[CORE-Bench](https://arxiv.org/abs/2409.11363)** asks whether agents can support computational reproducibility. **[EXP-Bench](https://arxiv.org/abs/2505.24785)** asks a more uncomfortable question: can AI actually conduct AI research experiments, rather than merely describe them? **[ResearchEnvBench](https://arxiv.org/abs/2603.06739)** highlights an especially underappreciated failure mode: many agents fail before the first experiment even begins because they cannot build the software environment needed to run it.

That last issue sounds technical and minor until you actually try to do this work. Then it becomes obvious that some of the hardest parts of "auto research" are also the least photogenic: dependencies, CUDA versions, broken builds, hidden assumptions in old codebases, mismatched hardware, and missing documentation.

I've seen similar stories from other people building these systems. One example I found online involved setting up Karpathy's autoresearch workflow on a rented RTX Pro 6000, which uses Nvidia's Blackwell architecture. The original workflow had been run on H100s, which are Hopper-generation GPUs. That turned out to matter because only the newly released FlashAttention v4 supported Blackwell, and getting it to work required compiling from source with very little documentation. In the write-up, when the agent failed to install `flash-attn`, it did not really solve the compatibility problem; it quietly reduced the batch size and carried on as if nothing important had happened. The human operator had to push it back toward the real issue, add web search, and eventually step in to compile with the right architecture flags. Once the system got back to writing and editing code, it was fine. The weak point was the infrastructure around it.

## The real bottleneck is verification

After enough episodes like this, I stopped thinking of the main problem as model intelligence alone. The harder problem is **verification**.

Why are agents often decent at coding but weak at replication? Because code comes with feedback. If the program does not compile, the compiler tells you. If a test fails, the failure is local and explicit. Research is harsher. If an agent misreads a paper's core mechanism, or produces a training curve that looks plausible but does not actually match the original, nothing immediately lights up red. The feedback is sparse, delayed, and tangled across multiple stages.

You can break paper replication into four rough steps: understand the paper, write the code, train the model, validate the results. Those stages do not offer the same quality of feedback. Code writing usually provides the strongest signal. Training provides some. Paper understanding and final result validation often provide the weakest. Mistakes that happen early in those weak-signal stages then propagate all the way down.

That is a big part of why these systems often look better in demos than in the wild. They are operating in settings where polished output is easier to produce than grounded evidence.

You can see the literature adjusting to this reality. **[DeepResearchGym](https://arxiv.org/abs/2505.19253)** matters because it tries to create a transparent evaluation sandbox instead of another glossy end-to-end claim. **[Curie](https://arxiv.org/abs/2502.16069)** is interesting for the same reason: it pushes toward more rigorous and automated experimentation, not just free-form agent chatter. Critique papers such as **[Risks of AI Scientists](https://arxiv.org/abs/2402.04247)** and **[The More You Automate, the Less You See](https://arxiv.org/abs/2509.08713)** are worth taking seriously because they capture something practitioners run into very quickly. Smoother automation can make failure harder to notice.

And that has consequences beyond tooling.

## Research labor is being reshaped

It also means **research labor is being reshaped very quickly**.

A traditional lab does two things at once. It produces papers, and it trains future researchers. Junior students clean data, reproduce baselines, debug code, inspect metrics, and draft sections. That work has always been tedious, but it has also been formative. It is where people develop debugging instincts, experimental judgment, and the nose for when a result smells wrong.

Agents can now do a surprising amount of that work. They can analyze data distributions, summarize training curves, scaffold baselines, and write serviceable prose. Systems like **[The AI Scientist](https://arxiv.org/abs/2408.06292)** made this legible to a wider audience, and systems like **[EvoScientist](https://arxiv.org/abs/2603.08127)** and **[Agent Laboratory](https://arxiv.org/abs/2501.04227)** have kept pushing in the same direction. The result is that the lower layers of the research stack — routine coding, baseline-running, draft-writing, much of the mechanical experimentation — are getting cheaper very quickly.

That does not make the whole job automatable. What it does is make the scarce part of the job easier to see: judgment, or, to use the less academic word, **taste**.

Taste is what tells you which problem is worth chasing, which result matters, which anomaly is real, which "new idea" is just an old one in a fresh wrapper, and which line of work is already exhausted even if the benchmark still has room for another 0.3 percent. Models are getting better at execution. They are still much worse at deciding what is worth executing.

## AI compresses the middle. Humans own the ends.

That realization changed how I think about research tools. I stopped trying to build a system that replaces the researcher and started trying to build one that **amplifies judgment**.

In practice, that meant rebuilding my own workflow. Instead of asking an agent to run everything end to end and then hoping the output is real, I use it more like a research partner. It helps me skim and translate faster, collect notes into an evolving idea document, and push implementation and experiments onto a server while I stay focused on direction and review. The agent compresses execution. I spend more time on selection, framing, and interpretation.

That is the most useful near-term model I've found. Not "AI replaces the scientist," but **AI compresses the expensive middle of the workflow**.

Once you start from there, several downstream questions become hard to avoid.

One is authorship. Right now, academic credit often tracks labor: who ran the experiments, who wrote the code, who drafted the paper. But if an agent can do much of that in hours, those categories get blurry fast. What exactly does "contributed to the experiments" mean when the experiments were launched and monitored through an API? What does second authorship represent when the execution layer is heavily automated?

My guess is that contribution will shift upward, toward the parts that remain difficult to automate: defining the problem, choosing the right evidence, spotting the signal in noisy results, noticing when something is wrong, and providing the oversight that keeps the work honest.

There is also a training problem buried in all this. Many of the instincts that make a strong senior researcher were learned by doing exactly the work that is now being automated. If junior researchers no longer spend years debugging, reproducing, and interpreting messy experiments, then we will need a new answer to a very old question: how do people learn scientific judgment?

## Lessons from building these systems

A few technical lessons from building these systems are worth stating plainly.

**Context rot is real.** A single agent can drown in its own history. Tool outputs, debug traces, long instructions, and partial plans pile up until the system forgets what mattered. I used to worry that multi-agent handoffs would fragment context. In practice, one giant context can be just as destructive. Clean main context, specialized subagents, and compact returns work much better.

**Memory is not truth.** Persistent memory helps only if the stored material is reliable. If the system stores a wrong conclusion, that error does not stay in the past. It comes back later wearing the costume of authority. That is why memory governance matters more than memory accumulation.

**Novelty checking needs infrastructure, not vibes.** Searching arXiv alone is not enough. Prompting alone is not enough. If you want agents to judge whether an idea is actually new, you need better retrieval, stronger provenance, and a way to replay how the conclusion was reached.

**Papers themselves can mislead agents.** Papers are narratives. They tell the clean version of the story. The most important details are often in the code, the appendix, or the parts that authors compress away. Agents are good at following the story on the page. They are much worse at catching where the implementation diverges from the narrative. That is one reason replication benchmarks matter so much.

## Where this goes

I do not think we are about to get the fully autonomous scientist people keep imagining. Not yet. But the field is moving beyond toy workflow demos. The progress that matters most is not just bigger models with smoother prose. It is better infrastructure: replayable execution, environment-aware benchmarking, phase-specific verification, stronger harnesses, memory governance, and forms of oversight that preserve visibility without requiring constant babysitting.

So I keep ending up in the same place. The future of auto research probably is not a single super-agent that replaces the lab. It is a stack: better tools, better execution environments, better checks, and humans who stay responsible for taste, direction, and honesty.

Auto research is real. It already works well enough to change how research gets done. But it does not remove the need for scientists. If anything, it makes the human role sharper.

When execution gets cheap, the value moves upstream.

What matters then is not whether you can produce another experiment faster than a machine. It is whether you know which experiment is worth running in the first place.

---

# 自动科研是真的，只是和人们想的不一样

过去几个月，我大部分时间都在构建和使用自动科研 agent：能检索文献、写代码、跑实验、写论文，而且需要的人工干预少得惊人。这个方向的最新工作我读了不少，API 费用也烧了不少。足够让我亲身体会到: demo 止步的地方，真正的问题才刚开始。我们构建的两个测试系统：**[Research Copilot](https://daidong.github.io/post.html?slug=introducing-research-copilot)** and **[Research Assistant Mode](https://daidong.github.io/post.html?slug=introducing-ram-desktop)**

简单说：自动科研是真的，而且进步很快。但它没有在取代研究者，它在改变人的精力应该花在哪。

---

## 流程跑得通，执行靠不住

这一点有时不容易察觉，因为表面现在看起来已经很光鲜了。AI Scientist、Agent Laboratory、EvoScientist 这些系统已经展示了 LLM agent 能走完一个研究项目的完整外壳：读论文、提 idea、写代码、跑实验、分析结果、起草手稿。如果只看流程图，未来似乎已经板上钉钉。

但实际上，走完研究的步骤和做出可靠的科学是两回事。

我觉得最准确的描述仍然是**流程跑得通，执行靠不住**。这些系统经常能产出论文形状的东西，但远不能可靠地产出你愿意信赖的科学。一张漂亮的图可能来自一个有 bug 的 pipeline；一份精致的综述可能漏掉了那篇推翻整个前提的论文；一个结果章节可以写得信心满满，底下的实验其实根本没跑过。

我不认为这是什么罕见的失败模式。当任务奖励"看起来合理的叙述"胜过"有根据的执行"时，这更像是这些系统出错的默认方式。

最近的 benchmark 也指向同一个方向。CORE-Bench 考察 agent 能否支持计算可复现性。EXP-Bench 问了一个更让人不舒服的问题：AI 能不能真正做 AI 研究实验，而不仅仅是描述实验？ResearchEnvBench 则揭示了一个特别被低估的失败模式：很多 agent 在第一个实验开始之前就失败了，因为它们搭不出运行实验所需的软件环境。

最后这个问题听起来又技术又不起眼，直到你真的去做这件事。然后你会发现，"自动科研"里最难的一些部分恰恰也是最不上相的：依赖关系、CUDA 版本、编译失败、旧代码库里的隐含假设、硬件不匹配、文档缺失。

我见过其他做这类系统的人遇到类似的故事。一个在线案例是在租的 RTX Pro 6000（Nvidia Blackwell 架构）上跑 Karpathy 的 autoresearch 工作流。原始工作流是在 H100（Hopper 架构）上跑的。这个差异很关键，因为只有刚发布的 FlashAttention v4 才支持 Blackwell，而且必须从源码编译，文档几乎没有。在那篇记录里，agent 装不上 `flash-attn` 之后并没有真正解决兼容性问题——它悄悄把 batch size 改小，然后若无其事地继续跑了。人类操作者不得不把它拉回正题，加上网页搜索，最后还是自己下场用正确的架构参数编译的。回到写代码和改代码的环节后，agent 就没问题了。薄弱点在于周围的基础设施。

## 真正的瓶颈是验证

经历了足够多这样的事情之后，我不再把主要问题单纯归结为模型智能了。更难的问题是**验证**。

为什么 agent 写代码还行但复现论文很弱？因为代码自带反馈。程序编译不过，编译器会告诉你。测试失败了，失败是局部的、明确的。科研更残酷。如果 agent 误读了论文的核心机制，或者生成了一条看起来合理但实际上跟原始结果对不上的训练曲线——没有任何东西会立刻亮红灯。反馈是稀疏的、延迟的、跨阶段纠缠在一起的。

你可以把论文复现拆成四步：理解论文、写代码、训练模型、验证结果。这些阶段提供的反馈质量并不一样。写代码通常信号最强，训练稍次，论文理解和最终结果验证往往最弱。早期弱信号阶段犯的错误会一路传播到最后。

这在很大程度上解释了为什么这些系统在 demo 里比在实战中好看得多。它们运行在"做出漂亮的输出"比"拿出有根据的证据"更容易的环境里。

文献也在适应这个现实。DeepResearchGym 之所以重要，是因为它试图创建一个透明的评估沙盒，而不是又一个光鲜的端到端声明。Curie 有意思也是同样的原因：它推动的是更严谨的自动化实验，而不只是 agent 自由发挥。Risks of AI Scientists 和 The More You Automate, the Less You See 这类批评性论文值得认真对待，因为它们捕捉到了实践者很快就会撞上的东西：更丝滑的自动化可以让失败更难被察觉。

而这带来的后果远不止工具层面。

## 科研劳动正在被快速重塑

这也意味着**科研劳动正在被快速重塑**。

一个传统实验室同时在做两件事：产出论文，培养未来的研究者。低年级的学生洗数据、复现 baseline、debug 代码、检查指标、起草段落。这些工作一直很枯燥，但也一直有塑造性。正是在这里，人们培养出了 debug 直觉、实验判断力、以及对"结果不对劲"的嗅觉。

Agent 现在能做其中惊人比例的工作。它们能分析数据分布、总结训练曲线、搭建 baseline、写出过得去的文字。AI Scientist 让更多人看到了这一点，EvoScientist 和 Agent Laboratory 继续推进着同一个方向。结果就是研究栈的下层——常规编码、跑 baseline、起草文稿、大量机械性的实验——正在迅速变得廉价。

这并不意味着整份工作可以被自动化。它做的是让这份工作中稀缺的部分变得更容易看清：判断力，或者用一个不那么学术的词，**taste**。

Taste 告诉你哪个问题值得追、哪个结果有意义、哪个异常是真的、哪个"新 idea"只是旧 idea 换了个包装、哪条研究线已经枯竭了——哪怕 benchmark 上还有 0.3 个点的空间。模型的执行能力越来越强，但在判断什么值得执行这件事上，它们还差得远。

## AI 压缩中间，人掌控两端

这个认识改变了我对科研工具的想法。我不再试图构建一个替代研究者的系统，而是开始构建一个**放大判断力**的系统。

在实践中，这意味着重建我自己的工作流。我不再让 agent 端到端地跑完所有东西然后祈祷输出是真的，而是把它更多地当作一个研究搭档。它帮我更快地浏览和翻译、把笔记汇集成一个不断演化的想法文档、把实现和实验推到服务器上跑——而我集中精力在方向和审查上。Agent 压缩执行，我把更多时间花在选择、框架和解读上。

这是我目前找到的最有用的近期模型。不是"AI 取代科学家"，而是 **AI 压缩工作流中间那段昂贵的部分**。

一旦从这里出发，几个下游问题就很难回避了。

一个是署名。目前学术署名往往跟踪劳动：谁跑了实验、谁写了代码、谁起草了论文。但如果 agent 几小时就能做完大部分，这些类别很快就模糊了。当实验是通过 API 发起和监控的，"参与了实验"到底是什么意思？当执行层被大量自动化后，二作代表什么？

我猜贡献会向上迁移，朝向那些仍然难以自动化的部分：定义问题、选择正确的证据、在嘈杂的结果中发现信号、注意到什么地方不对、以及提供让工作保持诚实的监督。

这里面还埋着一个培养问题。让一个资深研究者强大的那些直觉，很多是通过做那些正在被自动化的工作学会的。如果年轻研究者不再花几年时间 debug、复现、解读混乱的实验结果，那我们就需要为一个很老的问题找到新的答案：人是怎么学会科学判断力的？

## 构建这些系统的教训

从构建这些系统中学到的几条技术教训，值得直说。

**上下文腐败是真实的。** 单个 agent 会被自己的历史淹没。工具输出、debug 日志、长指令、半成品计划不断堆积，直到系统忘记什么是重要的。我以前担心多 agent 切换会切断上下文。实际上，一个巨大的上下文同样具有破坏性。干净的主上下文、专门的 subagent、压缩后的返回结果，效果好得多。

**Memory 不等于事实。** 持久化 memory 只在存储的内容可靠时才有帮助。如果系统存了一个错误的结论，这个错误不会留在过去。它会在未来披着权威的外衣回来。这就是为什么 memory 治理比 memory 堆积重要得多。

**新颖性检查需要基础设施，不是感觉。** 只搜 arXiv 不够，只靠 prompting 也不够。如果你希望 agent 判断一个 idea 是否真的新，你需要更好的检索、更强的溯源、以及一种回放结论是如何得出的方式。

**论文本身会误导 agent。** 论文是叙事。它们讲的是故事的干净版本。最重要的细节往往在代码里、附录里、或者作者压缩掉的部分里。Agent 很擅长跟着纸面上的故事走，但在发现实现与叙事之间的偏差这件事上差得多。这也是论文复现 benchmark 如此重要的原因之一。

## 未来的方向

我不认为我们即将得到人们一直想象的那种完全自主的科学家。还没到。但这个领域正在走出玩具级的工作流 demo。最重要的进展不只是更大的模型和更流畅的文字，而是更好的基础设施：可回放的执行、感知环境的 benchmark、分阶段的验证、更强的 harness、memory 治理、以及不需要全程盯着但保持可见性的监督形式。

所以我总是回到同一个结论。自动科研的未来大概不是一个替代整个实验室的超级 agent。它是一个栈：更好的工具、更好的执行环境、更好的检查机制，以及对 taste、方向和诚实负责的人。

自动科研是真的。它已经足够好，能够改变科研的做法。但它没有消除对科学家的需求。如果说有什么变化的话，它让人的角色变得更锐利了。

当执行变得廉价，价值就向上游迁移。

到那时重要的不是你能不能比机器更快地跑出下一个实验，而是你是否知道哪个实验一开始就值得跑。
