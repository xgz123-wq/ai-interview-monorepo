# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **部署状态**:已通过完整端到端部署验证(VM + Docker Compose + 13 张表 + 9 个迁移),8 个部署坑已修复 commit。复盘见 [docs/部署实战总结与面试弹药.md](docs/部署实战总结与面试弹药.md)。

## 项目结构

```
app/
├── api/          # 路由层(client/ + backoffice/)
├── schemas/      # Pydantic 模型
├── services/     # 业务逻辑(client/ + backoffice/ + common/)
├── models/       # SQLAlchemy ORM
├── core/         # 配置、Celery、安全
├── route/        # 路由注册中心(router_registry.py)
├── schedule/     # Celery 任务
└── db/           # 数据库会话
```

## 常用命令

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
docker compose exec app alembic upgrade head
docker compose exec app alembic revision --autogenerate -m "描述"
docker compose exec app python scripts/seed_position_templates.py
docker compose exec app python scripts/create_first_admin.py
python main.py                                    # API: settings.API_PORT
celery -A app.core.celery_app worker --loglevel=info
celery -A app.core.celery_app beat --loglevel=info
```

## 核心架构

1. **路由注册中心** [router_registry.py](app/route/router_registry.py):新接口必须注册到 `CLIENT_ROUTES` / `BACKOFFICE_ROUTES`,否则不生效
2. **AI 服务中枢** [ai_service.py](app/services/client/ai_service.py):统一封装所有 DeepSeek 调用(`parse_resume / analyze_resume / generate_questions / select_and_adapt_questions / evaluate_answer / generate_report`);`_extract_json` 三层容错
3. **题库 RAG** [interview_service.py](app/services/client/interview_service.py) `_generate_questions_with_rag` 三分支:
   - `≥total` → `select_and_adapt_questions`(AI 选题+微调)
   - `0<cnt<total` → `generate_with_seeds`(题库题作种子+AI 补)
   - `=0` → `generate_questions`(纯 AI 兜底)
   召回失败时放宽 `position_tag` 二次召回。**题库题携带 `bank_id / reference_answer / key_points` 全链路至评分**;pgvector 用 `cosine_distance` + `hnsw vector_cosine_ops`,改距离算子必须同步改索引
4. **岗位匹配 Agent** [position_agent_service.py](app/services/client/position_agent_service.py) + [position_agent_tools.py](app/services/client/position_agent_tools.py):LangChain `create_tool_calling_agent` + 5 个 `@tool` 串联;**工具 docstring 即 LLM schema**
5. **配置** [config.py](app/core/config.py):pydantic Settings + `.env`;Embedding 维度 `KNOWLEDGE_EMBEDDING_DIM=1024` 写死 `Vector(1024)` 列,批量 `BATCH_SIZE=25` 服务端硬限制
6. **异步/同步双版本**:业务用 `embed_text`(async),Celery 用 `embed_text_sync`(sync);**不要在 Celery 里 `asyncio.run` 包 async**

## 新增模块规范

| 场景 | 操作 |
|------|------|
| 新 API 路由 | `router_registry.py` 加 `RouteConfig` |
| 新 RAG 分支 | 改 `_generate_questions_with_rag`,绕过会断 `bank_id` 全链路 |
| 新 Agent 工具 | 加到 `POSITION_AGENT_TOOLS` + 同步 system prompt |
| 新 Celery 任务 | `app/schedule/jobs/` 新建后加进 `celery_app.py` 的 `include` |
| 改岗位模板字段 | 同步 `models/position_template.py` + `scripts/seed_position_templates.py` + `_calculate_match_score` 三处 |

## 端口(外部映射)

| 服务 | 端口 |
|------|------|
| API | 8006(`settings.API_PORT`) |
| PG | **5435**(原 5434) |
| Redis | 6382 |
| Nginx | 8080 |
| Flower | 5555 |

## 红线

- PG 镜像必须 `pgvector/pgvector:pg16`
- Embedding 维度硬编码 1024;换模型需 `ALTER TABLE ... TYPE vector(N)` + 跑 `reindex_all_questions_task`
- 9 个迁移版本(3 个补的);`alembic current` 期望 `b3a4c5d6e7f8 (head)`

## 技术栈

FastAPI + SQLAlchemy 2.x + PostgreSQL(pgvector) + Redis + Celery + Alembic + LangChain + DeepSeek + DashScope
