# AI Interview

一个面向求职场景的 **AI 模拟面试系统**。  
项目围绕“**简历解析 -> 岗位匹配 -> RAG 出题 -> AI 评分 -> 面试报告**”构建了完整闭环，重点体现了我在 **AI 应用开发、工程化落地、RAG 设计、Agent 工作流编排** 方面的能力。

---

## 项目简介

传统模拟面试系统通常只解决“出题”和“评分”，而这个项目进一步把 AI 放到了求职链路前面：

- 用户上传简历后，系统先调用 AI 解析简历并落库
- 基于岗位匹配 Agent，对候选人画像进行分析并推荐更适合的岗位方向
- 进入目标岗位的专项模拟面试
- 基于题库 RAG 召回高相关题目，并结合参考答案与采分点进行 AI 评分
- 输出结构化面试报告，帮助用户明确能力差距和下一步学习方向

这个项目不是单一 Prompt Demo，而是一个包含 **前端、后端、数据库、异步任务、向量检索、Agent 编排、Docker 部署** 的完整 AI 应用项目。

---

## 核心亮点

### 1. 面向真实业务的 AI 闭环

此项目实现了完整的求职场景闭环：

- 简历上传与解析
- 岗位匹配 Agent
- 题库 RAG 面试
- AI 评分与反馈
- 面试报告输出



### 2. 题库 RAG

项目中实现了两套 RAG，其中真正接入主业务的是 **题库 RAG**：

- 管理员维护结构化题库：题目、参考答案、采分点
- 将题目与参考答案拼接后做向量化
- 使用 `PostgreSQL + pgvector` 存储 embedding
- 面试发起时，结合岗位和简历技能做语义召回
- 当题库不足时，采用“二次召回 + AI 兜底补全”的策略保证流程稳定

相比纯 AI 生成题目，这种方式让题目更贴近岗位，也让评分更可控。

### 3. 评分不是“凭感觉”，而是基于题库标准答案

用户回答问题后，系统不会直接让大模型自由打分，而是把题库中的：

- `reference_answer`
- `key_points`

一起注入评分 Prompt，作为评分参考依据。  
这样可以显著提升评分稳定性，减少大模型“凭感觉评分”的不确定性。

### 4. 实现了岗位匹配 Agent，而不是单纯表单跳转

项目含有 **岗位匹配 Agent**功能，用于把“简历解析”和“模拟面试”连接起来。

它不是凭空推荐岗位，而是：

- 先读取已解析的结构化简历
- 构建候选人画像
- 再与系统中的岗位模板库做匹配
- 输出推荐岗位、推荐理由、能力差距和下一步建议

技术上使用了 **LangChain Tool Calling Agent**，并配合工具调用工作流来保证结果可解释、可调试。

### 5. 项目具备工程化

项目中体现了较完整的工程化思维：

- 前后端分离架构
- Docker Compose 本地一键启动
- PostgreSQL / Redis / Celery 异步任务协同
- 静态文件挂载与容器内服务通信
- API 分层、Service 分层、Schema 分层
- 向量检索、异步任务、SSE 流式输出


---

## 技术栈

### 后端

- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- pgvector
- Redis
- Celery
- Alembic
- Uvicorn

### AI / RAG / Agent

- DeepSeek API
- OpenAI Compatible SDK
- LangChain
- LangChain OpenAI
- DashScope Embedding
- RecursiveCharacterTextSplitter

### 前端

- Vue 3
- Vite
- Vue Router
- Pinia
- Axios

### 工程与部署

- Docker / Docker Compose
- Nginx
- Linux

---

## 系统架构

```text
[用户前端]
   ├─ 上传简历
   ├─ 岗位匹配
   ├─ 模拟面试
   └─ 查看报告
        │
        ▼
[FastAPI 后端]
   ├─ 简历解析服务
   ├─ 岗位匹配 Agent
   ├─ 面试服务
   ├─ 题库管理
   └─ 知识库管理
        │
        ├─ DeepSeek：简历解析 / 出题 / 评分 / 报告
        ├─ DashScope：Embedding
        ├─ PostgreSQL + pgvector：结构化数据 + 向量检索
        ├─ Redis：缓存 / Broker
        └─ Celery：异步任务
```

---

## 业务流程

### 1. 简历解析

用户上传 PDF 简历后，系统会：

1. 提取 PDF 文本
2. 调用 DeepSeek 解析成结构化简历
3. 生成简历分析结果
4. 将 `parsed_content` 与 `analysis` 写入数据库

### 2. 岗位匹配 Agent

Agent 主流程：

1. 读取已解析简历
2. 构建候选人画像
3. 匹配岗位模板
4. 获取岗位面试重点
5. 输出推荐岗位、推荐理由、能力差距和学习建议

### 3. 题库 RAG 出题

发起面试时，系统会：

1. 根据目标岗位 + 简历技能构造检索 query
2. 调用 DashScope Embedding 生成 query vector
3. 在 `question_bank` 中用 `pgvector cosine_distance` 召回候选题
4. 如果候选题足够，由 AI 选题并微调
5. 如果候选题不足，触发二次召回或 AI 兜底补全

### 4. AI 评分

用户提交回答后，系统会：

1. 获取当前题对应的 `reference_answer` 和 `key_points`
2. 构造评分 Prompt
3. 调用 DeepSeek 评分并流式返回反馈
4. 保存单题得分、反馈、整场报告

---

## 项目结构

```text
ai-interview/
├─ ai-interview-backend/     # FastAPI + PostgreSQL + Redis + Celery
├─ ai-interview-frontend/    # 用户端前端
├─ ai-interview-admin/       # 管理端前端
├─ 面试要点.md               # 项目口述与面试整理
├─ 项目RAG实现原理.md         # RAG 技术链路说明
└─ Agent规划书.md            # 岗位匹配 Agent 规划与收敛版说明
```

---



## 工程化设计亮点

### 分层清晰

后端采用较清晰的分层：

- `api`：接口层
- `schemas`：请求/响应模型
- `services`：业务逻辑层
- `models`：数据库模型

这样做的好处是：

- 业务逻辑更集中
- 便于单独维护 RAG、Agent、简历、面试等模块
- 后续扩展更自然

### AI 能力统一封装

`ai_service.py` 不是简单的模型调用文件，而是项目里的 **AI 能力中枢**，统一封装了：

- 简历解析
- 简历分析
- 面试出题
- 回答评分
- 流式反馈
- 报告生成
- 题库补题与微调

### Agent 采用工具调用工作流

岗位匹配 Agent 不是“一个大 Prompt 全部搞定”，而是显式拆成多步工具调用：

- `get_parsed_resume`
- `build_candidate_profile`
- `match_positions`
- `get_position_interview_focus`
- `start_mock_interview`

这样结果更稳定，也便于调试和展示 Agent 的执行过程。

### 兼顾开发效率与可部署性

项目提供 Docker Compose 开发环境，能够快速拉起：

- App
- PostgreSQL
- Redis
- Celery Worker
- Celery Beat

对 AI 应用项目来说，这一点很重要，因为它体现的是“可运行、可联调、可部署”的完整能力。

---

## 启动方式

> 详细部署（VM 准备、Docker 加速、共享文件夹、镜像加速）见 [ai-interview-backend/部署文档.md](ai-interview-backend/部署文档.md)；
> 从旧版 `ai-interview` 升级并保留数据见 [ai-interview-backend/升级部署文档.md](ai-interview-backend/升级部署文档.md)。

### 前置条件

| 依赖 | 版本 | 用途 |
|------|------|------|
| Docker + Docker Compose V2 | 最新 | 后端容器编排（项目内含 `docker-compose-linux-x86_64` 离线包） |
| Node.js | 18+ | 前端 Vite dev server |
| **DeepSeek API Key** | - | 简历解析 / 出题 / 评分 / 报告（[申请](https://platform.deepseek.com/)） |
| **DashScope API Key** | - | 题库/知识库 Embedding（[申请](https://dashscope.console.aliyun.com/)，开通"通用文本向量"） |

少了 `DASHSCOPE_API_KEY` 时，AI 闭环跑不通——题库和知识库向量化全部失败。

### 1. 首次启动后端

```bash
cd ai-interview-backend

# 1) 复制环境变量模板,并填入 DEEPSEEK_API_KEY / DASHSCOPE_API_KEY
cp .env.example .env
# Windows 端用编辑器打开 .env,保存后 VM 端实时生效

# 2) 构建并启动所有服务(app / celery / pg / redis,首次需要拉镜像)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# 3) 等所有容器 Up (healthy) 后,跑迁移建表
docker compose exec app alembic upgrade head
# 期望输出:b3a4c5d6e7f8 (head),13 张表

# 4) 灌岗位模板(岗位匹配 Agent 的依赖库,不灌则 Agent 跑空)
docker compose exec app python scripts/seed_position_templates.py

# 5) 创建后台管理员账号
docker compose exec app python scripts/create_first_admin.py
# 默认账号:admin@ai-interview.com / ai-interview&admin

# 6) 健康检查
curl http://localhost:8006/api/v1/config/health
# 期望:{"code":200,"message":"Success","data":{"status":"healthy"}}
```

### 2. 启动用户端前端(端口 3000)

```bash
cd ai-interview-frontend
npm install
npm run dev
```

`vite.config.js` 中 `/api` 与 `/uploads` 已 proxy 转发到后端 `:8006`,无需额外配置。

### 3. 启动管理端前端(端口 3001,新开终端)

```bash
cd ai-interview-admin
npm install
npm run dev
```

### 访问地址

| 端 | 地址 |
|----|------|
| 用户端 | http://localhost:3000 |
| 后台管理 | http://localhost:3001 |
| 后端 API 文档 | http://localhost:8006/docs |
| 后端健康检查 | http://localhost:8006/api/v1/config/health |
| Flower(Celery 监控,可选) | http://localhost:5555(需 `--profile monitoring` 启动) |

### 端口一览

| 服务 | 端口 |
|------|------|
| FastAPI 后端 | 8006 |
| PostgreSQL(含 pgvector) | **5435**(开发标准) |
| Redis | 6382 |
| 用户端 / 管理端 | 3000 / 3001 |
| Nginx | 8080(dev 默认关闭) |

### 默认账号

| 角色 | 邮箱 | 密码 |
|------|------|------|
| 后台管理员 | `admin@ai-interview.com` | `ai-interview&admin` |

普通用户通过用户端注册页面自行注册(邮箱 + 密码,无需邮箱验证)。

### 日常启动速查

后端容器配置了 `restart: unless-stopped`,VM 重启后会自动恢复,日常只需:

```bash
# 启动后端(已在运行时此命令幂等)
cd ai-interview-backend
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 关闭后端
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
# 注:不要加 -v,否则数据库卷会被删,数据全丢
```

前端每次 `npm run dev` 即可。

### 初始化 RAG 数据(管理员首次操作)

完成上面三步后,登录后台(http://localhost:3001)完成 RAG 初始化,否则出题/评分会降级:

1. **题库管理** → 批量导入面试题(字段:题目 / 参考答案 / 采分点 / 岗位标签 / 难度)→ 重建索引
2. **知识库管理** → 上传 Markdown / PDF / DOCX → 系统自动切片 + DashScope Embedding
3. **岗位模板管理** → 验证 10 条模板已 seed(可手动微调)



---

### 系统截图
1.Rag题库准备,导入面试题目并向量化
<img width="1910" height="925" alt="1 导入题目" src="https://github.com/user-attachments/assets/e3625ef8-4f79-4300-8848-9b37d51b41e0" />

<img width="1910" height="925" alt="2 向量化" src="https://github.com/user-attachments/assets/29b6dc4e-23ef-43ce-9fab-62fd88c5a0a6" />



2.Rag知识库准备,上传知识文档并向量化
<img width="1910" height="925" alt="3 知识库" src="https://github.com/user-attachments/assets/c0582c25-a833-4107-af30-916b5a916227" />

<img width="1910" height="925" alt="4 知识库上传与向量化" src="https://github.com/user-attachments/assets/39f24e81-5c52-410d-97bd-d4c534778f03" />

3.岗位模板(Agent将会参考岗位模板进行岗位匹配,增强匹配效果)

<img width="1910" height="925" alt="5 岗位模板" src="https://github.com/user-attachments/assets/a913c109-2f30-44b4-8001-1380329ace1e" />

4.简历上传与解析
<img width="1910" height="925" alt="6 简历上传" src="https://github.com/user-attachments/assets/7ed998f7-ccae-4805-bcb3-8f966d184d63" />

<img width="1910" height="925" alt="7 简历解析" src="https://github.com/user-attachments/assets/dfc489cc-3215-489d-9549-8f44334b92c5" />


### 两种面试途径，一个是简历解析完毕后直接启动面试，另一个是让Agent进行岗位匹配，启动面试，针对性更强

### 启动面试途径1,直接开始

1.解析完成后，点击开始面试
<img width="689" height="1211" alt="8 解析结果" src="https://github.com/user-attachments/assets/7e4ca082-61c8-4c99-aa71-18f56a45bbc5" />

2.开始面试
<img width="2552" height="1316" alt="9 开始面试" src="https://github.com/user-attachments/assets/25eb8b95-6481-43f8-91ee-2e81c1812e06" />

3.面试场景(题目来源于Rag题库)
<img width="2552" height="1316" alt="10 面试场景" src="https://github.com/user-attachments/assets/eba566a4-cca0-4f1f-a8cd-2e260ae59f4c" />

4.面试报告生成
<img width="2552" height="1316" alt="11 生成报告" src="https://github.com/user-attachments/assets/201f027c-10e7-4d60-9da4-b4c1e9b50147" />



### 启动面试途径2,通过Agent启动

1.Agent读取已经解析好的简历，重新构建更精细的候选人画像，从而精准匹配后台预先准备好的岗位模板

<img width="2552" height="1316" alt="12 Agent匹配" src="https://github.com/user-attachments/assets/61c457b3-cd40-4e17-8ff0-7585e45d0108" />

2.候选人画像汇总与建议，以及岗位匹配结果
<img width="2552" height="1316" alt="13 匹配结果1" src="https://github.com/user-attachments/assets/3f093e0d-a834-4a85-9e5c-d663749f5169" />

<img width="2552" height="1316" alt="14 匹配结果2" src="https://github.com/user-attachments/assets/3e45ae29-54fd-41da-ad40-69c776c0f86e" />

<img width="2552" height="1316" alt="15 匹配结果3" src="https://github.com/user-attachments/assets/8ea95bd4-9408-4cf8-a036-bfe28c857359" />


3.进入面试(Agent调用面试功能)

<img width="2552" height="1316" alt="16 启动并进入面试" src="https://github.com/user-attachments/assets/697d3683-e85e-49df-81ee-d375fbc17b78" />

4.面试记录

<img width="2552" height="1316" alt="17 面试记录" src="https://github.com/user-attachments/assets/0bc91b00-196c-4d65-ba5e-591ab489876a" />








