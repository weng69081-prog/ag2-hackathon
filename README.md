# Life Sandbox — 多智能体职业路径咨询系统

<p align="center">
  <img src="https://img.shields.io/badge/AG2_Beta-多智能体-6366f1?logo=automattic" alt="AG2 Beta">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-1.0-009688?logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/赛道-multi--agent-8b5cf6" alt="赛道">
</p>

> 由主策展人（Coordinator）与批评家（Critic）协作的智能职业规划工具，基于 AG2 Beta 框架，构建完整的 **多智能体辩论闭环**。

---

## ✨ 项目亮点

本项目在 AG2 Hackathon 原版 Life Sandbox 基础上，完成了以下关键改造：

### 🆕 激活 Critic Agent（批评家）
原版代码中已预留 Critic Agent 的定义但未接入主流程。本改造将其**全面激活**，形成「生成 → 批评 → 修订」的辩论机制，让每条职业路径都经过多轮推敲。

### 🆕 新增 Action Planner Agent（行动规划师）
在最终排名生成后，为每条职业路径自动生成包含 **课程学习、项目实践、社交活动** 等具体行动方案，让规划真正落地。

### 🔧 SSE 数据流修复与前端优化
修复了直播数据推送（SSE）中 Critic 评测数据和行动计划的传输问题，确保前端能完整展示所有智能体的输出。

### 🤖 多智能体协作架构

| 智能体 | 职责 |
|--------|------|
| **Coordinator（主策展人）** | 根据用户背景生成初步的职业路径建议 |
| **Critic（批评家）** | 审视输出，从可行性、个性化等角度提出质疑 |
| **Decision Agent（修订决策）** | 综合辩论结果，输出修订后的最终方案 |
| **Action Planner（行动规划）** | 为每条路径生成可执行的行动清单 |

---

## 🚀 快速启动

```bash
# 1. 克隆仓库
git clone https://github.com/weng69081-prog/ag2-hackathon.git
cd ag2-hackathon/life-sandbox

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 3. 安装依赖
uv sync

# 4. 启动服务
uv run uvicorn backend:app --reload --port 8765

# 5. 打开浏览器
open http://localhost:8765
```

---

## 📁 项目结构

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

## 🛠 技术栈

- **框架：** AG2 Beta（原 AutoGen 2.0）
- **后端：** Python + FastAPI + Pydantic
- **前端：** 纯 HTML + JavaScript（无构建工具）
- **AI 模型：** 兼容 Gemini / Qwen 等多种模型

---

## 📚 交付文档

- `曾怡嫚_C5-AG2_AI日志.md` — AI 协作开发日志（完整记录改造过程）
- `曾怡嫚_C5-AG2_拿来说明.md` — 借鉴与改动清单