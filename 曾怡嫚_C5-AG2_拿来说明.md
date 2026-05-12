# C5-AG2 拿来说明
**项目**：Life Sandbox 多智能体职业咨询系统
**姓名**：曾怡嫚
## Fork 源
- 原作者仓库：https://github.com/myaooo/ag2-hackathon
- 原项目名：Life Sandbox
- 原队长：Rui
## 借鉴片段
1. 整体 Agent 架构：借鉴原项目的 5 个评估 Agent 并行设计（Career/Finance/Risk/Lifestyle + Coordinator）。
2. Critic Agent 定义：原作者在 agents.py 中已预留 Critic 的 schema 和 prompt，但未接入主流程。本改造将其激活并整合。
3. SSE 流式输出：原项目的 /analyze/stream_SSE 端点中启用了 Critic，本改造将其逻辑移植到主表单提交流程。
## 我的改动与新增
1. 激活 Critic Agent：将 Critic 从"预留但未启用"改为"主流程必经过的一环"，形成 决策→批评→修订 的辩论机制。
2. 新增 Action Planner Agent：在最终排名生成后，为每条职业路径自动生成包含课程学习、项目实践、社交活动的 4 条具体行动计划，以 action_plan 字段返回并渲染在路径卡片底部。
3. 修改 agents.py：去掉强制 structured output，改为自由文本 + json.loads 解析，以兼容多种模型；新增 build_action_planner 函数。
4. 修改 backend.py：重构 /simulate 端点和 /analyze/stream (SSE) 端点的调用链，引入 _parse_reply() 统一处理 Agent 返回，并增加 Critic 评审横幅与 Action Plan 的数据推送。
5. 修改 frontend.html：新增 Critic 总结渐变紫色横幅（#critic-summary-bar）和行动计划灰底蓝边卡片（renderActionPlanHtml），均通过 JS 模板字符串动态渲染。
6. 模型适配：从 Google Gemini 切换至 Qwen2.5-32B-Instruct，解决地区限制与结构化输出兼容问题。
7. 仓库整理：添加 README.md、完善 .gitignore，确保 API Key 不泄露。