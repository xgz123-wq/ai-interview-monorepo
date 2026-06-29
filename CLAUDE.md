# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目定位

AI 模拟面试系统的**用户端**(Vue 3 + Vite + Pinia + Vue Router),面向求职者。管理端在 `../ai-interview-admin/`,后端在 `../ai-interview-backend/`。

跨项目架构与部署见仓库根 [CLAUDE.md](../CLAUDE.md) 与 [docs/部署实战总结与面试弹药.md](../docs/部署实战总结与面试弹药.md)。

## 常用命令

```bash
npm install
npm run dev        # 开发服,端口 3000
npm run build      # 生产构建
npm run preview    # 预览生产包
```

> 实际部署用 `npm`(已在 [部署文档.md 第三步](../ai-interview-backend/部署文档.md) 落地);`pnpm` 也兼容。`vite.config.js` 里的 `target` 是 VM IP,改 IP 必须同步两处(本项目 + admin)。

## 目录结构

```
src/
├── main.js              # 入口:createApp + Pinia + Router
├── App.vue              # 根布局:登录后渲染顶栏 + router-view
├── router/index.js      # 路由表 + 登录守卫
├── stores/auth.js       # Pinia auth store(token + userInfo 持久化)
├── style.css
└── api/
    ├── request.js       # 唯一的 axios 实例
    ├── auth.js          # /auth/register、/auth/login、/auth/me
    ├── user.js          # 个人资料/头像/改密
    ├── resume.js        # 简历上传/列表/详情
    ├── interview.js     # 面试核心:启动/答题/答题流式/报告
    └── positionAgent.js # 岗位匹配 Agent + Agent 启动面试

views/
├── Login.vue / Register.vue
├── Dashboard.vue              # 面试记录列表
├── ResumeUpload.vue           # 简历上传 + 解析结果
├── Interview.vue              # 面试进行中(聊天 UI + 准备动画 + 流式评分)
├── Report.vue                 # 面试报告
├── PositionMatch.vue          # 岗位匹配 Agent 可视化
└── Profile.vue                # 个人中心
```

## 核心架构

1. **API 客户端** [api/request.js](src/api/request.js):唯一 axios 实例;`baseURL: '/api/v1'`(vite proxy → 8006);响应拦截器业务 `code === 200` 返回 `data.data`(调用方直接拿到业务载荷,**不再 `.data.data` 解包**)
2. **鉴权** [stores/auth.js](src/stores/auth.js):setup-style Pinia + 双重 token(access + refresh),6 个字段持久化到 localStorage;刷新页面不丢登录态
3. **流式评分** [api/interview.js](src/api/interview.js) `submitAnswerStream`:**不走 axios**,用原生 `fetch + ReadableStream` 读 SSE;端点 `POST /api/v1/interviews/:id/answer/stream`,事件 `chunk / done / error`。**新加流式端点保持这个模式**
4. **Vite** [vite.config.js](vite.config.js):端口 3000;`/api` 代理后端 8006;`/uploads` 也代理(头像)

## 启动面试(两条路径)

| 路径 | 入口 | 关键 API |
|------|------|----------|
| 直接面试 | ResumeUpload.vue 上传简历 → 解析结果页填参数 → 启动 | `uploadResume` → `startInterview` |
| Agent 匹配后再面试 | PositionMatch.vue 选简历 → 跑 Agent → 看 Top 1 → 点"启动面试" | `matchPositions` → `startInterviewFromAgent` |

两种路径最终都跳到 `/interview/:id`。

## 业务约定

- **Agent 调用慢**:`matchPositions` 超时 180s(Agent 5 个工具 + DeepSeek 3-4 次调用),`startInterviewFromAgent` 120s;普通面试 60s,上传简历 120s。**不要把超时改小**
- **岗位匹配是核心体验**:PositionMatch 页面用进度条 + emoji 可视化 Agent 5 步工作流,改 UI 时保留可视化元素
- **流式端点不走 axios**
- **相对路径头像**:`stores/auth.js` 相对路径直接走 vite proxy,不拼 host
- **LocalStorage 字段**:`token/refreshToken/userEmail/userId/userName/userAvatar` 6 个 key,改时同步 `setAuth/setUserInfo/logout` 三处

## 开发约定

- Vue 3 `<script setup>`,所有页面统一用 `setup`
- API 走 `api/*` 模块的具名导出,不在页面里直接 `axios.get`
- 路径别名:无(Vite 默认 `@` 也没配)
- 无 ESLint / Prettier / 测试框架(仓库无),新增按官方 Vue + Vite 约定

## 联调启动

```bash
cd ../ai-interview-backend
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
cd ../ai-interview-frontend
npm install
npm run dev   # http://localhost:3000
```

## 技术栈

Vue 3.4 + Vite 5 + Vue Router 4 + Pinia 2 + Axios 1.7
