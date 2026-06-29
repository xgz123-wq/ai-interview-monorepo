# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目定位

AI 模拟面试系统的**管理端**(Vue 3 + Vite + Pinia + Vue Router),面向运营/管理员。用户端在 `../ai-interview-frontend/`,后端在 `../ai-interview-backend/`。

跨项目架构与部署见仓库根 [CLAUDE.md](../CLAUDE.md) 与 [docs/部署实战总结与面试弹药.md](../docs/部署实战总结与面试弹药.md)。

## 常用命令

```bash
npm install
npm run dev        # 开发服,端口 3001
npm run build      # 生产构建
npm run preview    # 预览生产包
```

> 实际部署用 `npm`(已在 [部署文档.md 第三步](../ai-interview-backend/部署文档.md) 落地);`pnpm` 也兼容。`vite.config.js` 里的 `target` 是 VM IP,改 IP 必须同步两处(本项目 + frontend)。

## 目录结构

```
src/
├── main.js              # 入口:createApp + Pinia + Router
├── App.vue              # 根布局:登录后渲染 sidebar + router-view
├── router/index.js      # 路由表 + 登录守卫
├── stores/auth.js       # Pinia auth store(token 持久化)
├── style.css
└── api/
    ├── request.js       # 唯一的 axios 实例
    └── index.js         # 业务模块 API 集合

views/
├── Login.vue / Dashboard.vue
├── Users.vue
├── Interviews.vue / InterviewDetail.vue
├── QuestionBank.vue / QuestionBankImport.vue / QuestionBankTest.vue
├── Knowledge.vue / KnowledgeDetail.vue / KnowledgeTest.vue
└── PositionTemplate.vue
```

## 核心架构

1. **API 客户端** [api/request.js](src/api/request.js):唯一 axios 实例;`baseURL: '/api/v1/backoffice'`(vite proxy → 8006);响应拦截器业务 `code === 200` 返回 `data.data`(调用方直接拿到业务载荷,**不再 `.data.data` 解包**)
2. **API 集合** [api/index.js](src/api/index.js):按业务域分组导出 `authApi / userApi / interviewApi / questionBankApi / positionTemplateApi / knowledgeApi`
3. **鉴权** [stores/auth.js](src/stores/auth.js):setup-style Pinia;token 持久化到 `localStorage`(`admin_token` / `admin_email`)
4. **Vite** [vite.config.js](vite.config.js):端口 3001;`/api` 代理后端 8006

## 业务页面

| 页面 | 路径 | 职责 |
|------|------|------|
| Dashboard | `/` | 4 张统计卡片(用户/简历/面试总数/已完成) |
| Users | `/users` | 用户管理、启用/禁用 |
| Interviews | `/interviews` | 面试记录列表 |
| InterviewDetail | `/interviews/:id` | 单场面试详情、问答回顾 |
| QuestionBank | `/question-bank` | 题库 CRUD + 批量导入 + 全量重建 |
| QuestionBankImport | `/question-bank/import` | 批量导入题目 |
| QuestionBankTest | `/question-bank/test` | 检索测试(调 `/question-bank/test-retrieve`) |
| Knowledge | `/knowledge` | 知识文档列表 |
| KnowledgeDetail | `/knowledge/:id` | 文档 chunk 列表 + 重新索引 |
| KnowledgeTest | `/knowledge/test` | 知识库检索测试 |
| PositionTemplate | `/position-templates` | 岗位模板(Agent 数据源) |

## 业务约定

- **题库是面试核心**:`QuestionBank.vue` 提供全量重建、检索测试入口;改召回参数(`QUESTION_BANK_MIN_SCORE / RECALL_FACTOR / TOP_K`)会影响后端 `_generate_questions_with_rag` 三分支
- **岗位模板是 Agent 数据源**:`PositionTemplate.vue` 维护的岗位进入 `match_positions` 候选池;改字段必须同步后端 `models/position_template.py` + `seed_position_templates.py` + `_calculate_match_score`
- **检索测试**直接调 `/test-retrieve` 端点,可验证 embedding 效果
- **全量重建按钮**触发后端 `reindex_all_questions_task` Celery 任务,**换 Embedding 模型后必跑**

## 开发约定

- Vue 3 `<script setup>`,所有页面统一用 `setup`
- API 走 `api/index.js` 导出的对象,不在页面里直接 `axios.get`
- 路径别名:无(Vite 默认 `@` 也没配)
- 无 ESLint / Prettier / 测试框架(仓库无),新增按官方 Vue + Vite 约定

## 联调启动

```bash
cd ../ai-interview-backend
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
docker compose exec app python scripts/seed_position_templates.py
docker compose exec app python scripts/create_first_admin.py
cd ../ai-interview-admin
npm install
npm run dev   # http://localhost:3001
```

默认登录账号见 `scripts/create_first_admin.py`(admin@ai-interview.com / ai-interview&admin)。

## 技术栈

Vue 3.4 + Vite 5 + Vue Router 4 + Pinia 2 + Axios 1.7
