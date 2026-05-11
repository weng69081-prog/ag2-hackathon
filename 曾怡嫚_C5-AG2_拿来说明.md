# C5-AG2 拿来说明
**项目**：Life Sandbox 多智能体职业咨询系统
**姓名**：曾怡嫚
## Fork 源
- 原作者仓库：https://github.com/myaooo/ag2-hackathon
- 原项目名：Life Sandbox
- 原队长：Rui
## 借鉴片段
1. 整体 Agent 架构：借鉴原项目的 5 个评估 Agent 并行设计（Career/Finance/Relationship/Health/Tech 五大维度），以及 Coordinator 统筹 → Decision 排名的核心流程。
2. Critic 预留定义：原作者在 agents.py 中已预留 Critic 的 schema 和 prompt（`build_critic()` 函数、`CritiqueOutput` 模型），但未接入主流程。本改造将其激活并整合。
3. SSE 流式输出：原项目的 /analyze/stream_SSE 端点中启用了 Critic，本改造将其逻辑移植到主表单提交流程，实现了 Coordinator → 5 评估 → Decision → Critic 批评 → 修订排名的完整流水线。
## 我的改动与新增
1. 激活 Critic Agent：将 Critic 从"预留但未启用"改为"主流程必经过的一环"，形成 决策→批评→修订 的辩论机制。
2. 修改 agents.py：去掉强制 structured output，改为自由文本 + json.loads 解析，以兼容多种模型。
3. 修改 backend.py：重构 /simulate 端点的调用链，引入 _parse_reply() 统一处理 Agent 返回，并增加 Critic 评审与修订总结的输出。
4. 模型适配：从 Google Gemini 迁移至 DeepSeek，解决地区限制与结构化输出兼容问题。
5. 仓库整理：添加 README.md、完善 .gitignore，确保 API Key 不泄露。