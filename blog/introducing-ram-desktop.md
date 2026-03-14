# Introducing RAM Desktop — A Research Assistant That Works With You

**Download:** [RAM Desktop (Google Drive)](https://drive.google.com/file/d/1Q3GdAlYBgr0EWdjQlzXT3FZz6nd_dH4g/view?usp=sharing)

---

RAM Desktop is a research assistant application I built for macOS. You give it a research question, and it breaks the work into tasks, searches for information, reads files, organizes evidence, and advances the project round by round — pausing at key checkpoints to ask for your review and approval before moving forward. Unlike a fully autonomous pipeline, RAM is designed to keep you in the loop: important results don't silently become "final." They wait for your decision in the Review Inbox, and each round ends with a summary that lets you choose whether to continue or stop.

RAM Desktop 是我为 macOS 开发的一款研究助手应用。你给它一个研究问题，它会拆分任务、查找资料、读取文件、整理证据，并一轮一轮推进研究进度——在关键节点暂停，等待你在 Review Inbox 里审核确认，每轮结束时也会给出小结，让你决定是否继续。它的设计出发点是"人在回路"：重要结论不会自动通过，每一步都留有你介入的空间，而不是一个把结果直接抛出来的黑箱。

The interface is organized around a few key views: the Dashboard for starting a research run and checking overall progress, the Taskboard to see what the agent is actively working on, the Console for live output and direct interaction, the Review Inbox for approval decisions, and the Evidence and Audit views for tracing where conclusions came from. The Settings page lets you configure your model API keys, context limits, and other advanced options — though the defaults are reasonable for most first runs.

应用界面围绕几个核心页面展开：Dashboard 用来发起研究和查看进度；Taskboard 展示当前任务拆分情况；Console 显示代理的实时输出，也支持你随时发消息介入；Review Inbox 是审核确认的入口；Evidence 和 Audit 页面则用来追溯结论的来源。Settings 页面可以配置模型 API Key、上下文限制等参数，但对大多数人来说默认值已经够用，第一次使用不需要改太多。

One thing I've found matters a lot in practice: the quality of the research question. A good question is specific, bounded, and answerable — it names what is being compared, under what conditions, and by what measure. For example: *"Does a model's tool-use behavior become more complex as prompts grow more cautious or skill-heavy? Compare GPT-5.2, GPT-5-mini, and GPT-5-nano using prompt complexity metrics derived from existing datasets."* Or: *"Using OpenEvolve as a base, can a reviewer agent that scores each evolved implementation replace fitness functions — and does ranking by reviewer score lead to better final algorithms?"* Both of these are tractable: they have a concrete subject, a comparison target, a measurable outcome, and a clear stopping condition. Questions like "research AI," "compare all major AI products," or "analyze AI trends across every industry" have none of those properties — they produce output that sprawls and never closes.

在实际使用中，研究问题的质量影响非常大。一个好问题需要具体、有边界、可回答——要写清楚比较的对象是什么、在什么条件下、用什么指标来衡量。比如："随着 prompt 变得更复杂、更谨慎或包含更复杂的 skill，模型调用工具的行为会不会也变得更复杂？用 GPT-5.2、GPT-5-mini 和 GPT-5-nano 分别测试，先从已有数据集里定义 prompt 复杂度指标，再进行对比。"又比如："基于 OpenEvolve，用一个 reviewer agent 对每次进化出的代码打分，直接用这个分数替代 fitness function 来驱动后续排序和进化——这样能不能选出更好的算法实现？"这两个问题都有明确的研究对象、比较目标、可测量的结果，以及清晰的终止条件。反过来，"帮我研究一下 AI""比较一下所有主流 AI 产品""分析未来科技趋势"这类问题什么都没有——研究会一直散开，永远收不住。

One more thing worth knowing: RAM is not a fire-and-forget tool. You can message the agent at any point during a run through the Console — to redirect its focus, ask it to dig deeper into a specific finding, push back on a conclusion, or shift the research toward a more interesting angle. The agent will take your input into account and adjust from there. This makes the tool feel less like running a script and more like working alongside a collaborator who can move faster than you but still needs your judgment to stay on track.

还有一点值得特别说明：RAM 不是那种"启动就不用管了"的工具。在运行过程中，你随时可以通过 Console 给代理发消息——让它重新聚焦某个方向、对某个发现深入追查、对某个结论提出质疑，或者把研究引向你觉得更有价值的角度。代理会把你的输入纳入考虑，从那里继续推进。用起来的感觉不像是在跑一个脚本，更像是在和一个能自己往前走、但还需要你把方向的协作者一起工作。

A note on safety: RAM can write and execute code as part of its research process — for example, running scripts to process data, test hypotheses, or produce charts. Its behavior is constrained to the project workspace you open, so it will not reach outside that folder. For most use cases this is safe, and you are shown a confirmation at first launch before any of this is enabled. That said, any actions taken by the agent are ultimately your responsibility. We are not liable for any loss, damage, or unintended effects caused by the agent during a run. Use a dedicated, clean project folder, and keep an eye on the Console if you are working with sensitive data or running code for the first time.

关于安全性需要说明一点：RAM 在研究过程中可能会编写并执行代码，例如运行脚本来处理数据、验证假设或生成图表。它的行为被限制在你所打开的项目目录内，不会触及该目录以外的文件。对大多数使用场景来说这是安全的，应用在首次启动时也会要求你确认后才会启用这些能力。但无论如何，代理执行的所有操作最终由你负责。由 agent 行为造成的任何损失、损坏或意外后果，我们不承担责任。建议使用一个专门、干净的项目文件夹；如果涉及敏感数据或第一次运行代码，请留意 Console 里的实时输出。

RAM Desktop is currently a macOS app distributed as a direct download. If you run into a security warning on first launch, right-click the app and choose Open, or allow it in System Settings → Privacy & Security. I'm continuing to work on it and welcome any feedback — feel free to reach out if you try it.

RAM Desktop 目前是一个 macOS 应用，通过直接下载分发。第一次打开时如果遇到系统安全提示，右键点击应用选择「打开」，或者在「系统设置 → 隐私与安全性」里放行即可。我仍在持续开发中，欢迎试用并给我反馈。
