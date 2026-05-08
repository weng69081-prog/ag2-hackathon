# Life Sandbox — 多智能体职业路径咨询系统

> 由主策展人（Coordinator）与批评家（Critic）协作的智能职业规划工具，基于 AG2 Beta 框架

**赛道：** multi-agent

---

## 改造亮点

本项目在原 AG2 Hackathon 模板基础上，**激活了原作者预留但未启用的 Critic Agent**，构建了完整的 **"生成 → 批评 → 修订"** 多智能体辩论闭环：

- **Coordinator（主策展人）**：负责根据用户背景生成初步的职业路径建议
- **Critic（批评家）**：审视 Coordinator 的输出，从可行性、完整度、个性化等角度提出质疑与改进建议
- **Multi-Agent 辩论协作**：Coordinator 与 Critic 交替发言，在多次辩论中不断收敛优化，最终输出高质量的职业规划方案

这一架构完美诠释了 AG2 框架的对话式多智能体协作能力，展示了"批判性思维"在 AI 系统中的落地实践。

<!-- 此处放 Demo 截图 -->

---

## 5 分钟快速启动

```bash
# 1. 克隆仓库
git clone https://github.com/weng69081-prog/ag2-hackathon.git
cd ag2-hackathon/life-sandbox

# 2. 配置环境变量
cp .env.example .env
# 然后编辑 .env 填入你的 API Key

# 3. 安装依赖
uv sync

# 4. 启动服务
uv run uvicorn backend:app --reload --port 8765

# 5. 打开浏览器访问
open http://localhost:8765
```

---

## 项目结构

```
life-sandbox/
├── agents.py        # 多智能体核心逻辑（Coordinator + Critic）
├── backend.py       # FastAPI 后端服务
├── schemas.py       # 数据模型定义
├── frontend.html    # 前端界面
├── ingest.py        # 知识库导入
├── DESIGN.md        # 设计文档
├── tests/           # 单元测试
├── .env.example     # 环境变量模板
└── pyproject.toml   # 项目配置与依赖
```

---

## 技术栈

- **框架：** AG2 Beta（原 AutoGen 2.0）
- **后端：** Python + FastAPI + Pydantic
- **前端：** 纯 HTML + JavaScript（无需构建工具）
- **AI 模型：** Gemini 2.5 Flash（通过 API 接入）