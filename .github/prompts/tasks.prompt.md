# SaltShark 开发任务清单

基于 PRD v1.7 和 Technical Specification v1.0 制定。

## Phase 1: MVP (最小可行产品) - Weeks 1-6

### 1.1 基础设施与环境搭建 (Week 1)
- [ ] **项目初始化**
  - [ ] 创建 Monorepo 结构 (Frontend, Backend, Devops)
  - [ ] 配置基础开发环境 (Dev Container, Pre-commit hooks)
  - [ ] **配置基础 CI 流水线 (GitHub Actions: Lint, Test)**
- [ ] **后端基础架构 (FasterApp)**
  - [ ] 初始化 FasterApp 项目结构 (使用 `uv` 包管理器)
  - [ ] 配置 TortoiseORM 和 PostgreSQL 连接 (集成 Aerich 迁移工具)
  - [ ] 配置 Redis 连接
  - [ ] 配置 Celery 异步任务队列
  - [ ] 实现统一的配置管理 (Pydantic Settings)
  - [ ] 实现统一的异常处理和日志记录
- [ ] **前端基础架构 (Next.js)**
  - [ ] 初始化 Next.js 16 + TypeScript 项目
  - [ ] 集成 shadcn/ui 组件库
  - [ ] 配置 TailwindCSS
  - [ ] 配置 Zustand 状态管理
  - [ ] 配置 React Query (TanStack Query)
  - [ ] 搭建基础 Layout (Sidebar, Header)

### 1.2 认证与用户系统 (Week 2)
- [ ] **后端认证集成**
  - [ ] 实现 JWT/Bearer Token 验证中间件
  - [ ] 集成 Keycloak (OIDC) 配置
- [ ] **用户管理集成**
  - [ ] 实现 `UserManagementClient` (对接外部用户 API)
  - [ ] 实现用户信息缓存 (`UserInfoService` + Redis)
  - [ ] 实现用户信息降级策略
  - [ ] 定义 `UserReference` 数据模型并迁移
- [ ] **前端认证集成**
  - [ ] 集成 Auth.js (NextAuth) 与 Keycloak
  - [ ] 实现登录/登出流程
  - [ ] 实现用户信息展示 (Header)

### 1.3 Salt API 集成与 Minion 管理 (Week 3-4)
- [ ] **Salt Master 集成**
  - [ ] 配置 Salt Master (External Auth, Rest CherryPy)
  - [ ] 实现 `SaltAPIClient` (Login, Minions, Keys, Run)
  - [ ] **实现 Salt API Mock Server (用于本地开发/测试)**
  - [ ] 实现 Salt Event Bus 监听器 (WebSocket 监听 Master)
- [ ] **Minion 数据管理**
  - [ ] 定义 `Minion` 数据模型
  - [ ] 实现 Minion 同步任务 (Sync Grains, Status)
  - [ ] 实现 Minion 列表 API (分页, 搜索, 筛选)
  - [ ] 实现 Minion 详情 API
- [ ] **Minion Key 管理**
  - [ ] 实现 Key 管理 API (List, Accept, Reject, Delete)
  - [ ] 前端：Minion 列表页面
  - [ ] 前端：Minion 详情页面
  - [ ] 前端：Key 管理操作交互

### 1.4 基础远程执行与 Dashboard (Week 5-6)
- [ ] **实时通信服务**
  - [ ] **搭建后端 Socket.IO Server**
  - [ ] **实现 Event Bus 到 Socket.IO 的消息转发逻辑**
  - [ ] 前端：集成 Socket.IO Client 并处理连接状态
- [ ] **基础远程执行**
  - [ ] 实现 `cmd.run` 执行 API
  - [ ] 实现执行结果解析与存储
  - [ ] 前端：简单的命令执行界面
  - [ ] 前端：执行结果实时展示 (基于 Socket.IO)
- [ ] **Dashboard**
  - [ ] 实现基础统计 API (Minion 总数, 在线数)
  - [ ] 前端：Dashboard 概览页面
- [ ] **MVP 集成测试**
  - [ ] 端到端流程测试 (Login -> List Minions -> Run Command)

---

## Phase 2: 完整功能 (Full Features) - Weeks 7-14

### 2.1 高级远程执行 (Week 7-9)
- [ ] **高级 Targeting 支持**
  - [ ] 后端：支持 Glob, Grains, Pillar, Compound 目标匹配
  - [ ] 前端：高级目标选择器组件
- [ ] **模块化执行支持**
  - [ ] 后端：扩展执行 API 支持多种 Salt 模块
  - [ ] 后端：实现模块白名单/参数验证
  - [ ] 前端：可视化命令构建器 (模块选择, 参数表单)
- [ ] **执行历史**
  - [ ] 定义 `Job` 数据模型 (扩展)
  - [ ] 记录所有执行历史
  - [ ] 前端：执行历史列表与详情

### 2.2 Job 管理 (Week 10-12)
- [ ] **Job 监控与管理**
  - [ ] 完善 `Job` 模型与状态机
  - [ ] 实现 Job 列表 API (按状态, 时间筛选)
  - [ ] 实现 Job 详情 API (包含每个 Minion 的返回结果)
  - [ ] 实现 Job 控制 API (Terminate Job)
- [ ] **前端 Job 管理**
  - [ ] Job 列表页面 (自动刷新)
  - [ ] Job 详情页面 (时间线, 结果展示)
  - [ ] 重新执行功能

### 2.3 细粒度权限系统 (Week 13-14)
- [ ] **OpenFGA 集成**
  - [ ] 部署 OpenFGA 服务
  - [ ] 定义 OpenFGA Schema (User, System, Minion, Job)
  - [ ] 实现 `PermissionService` (Check, Write Tuples)
  - [ ] 实现权限初始化脚本 (Bootstrapping)
- [ ] **权限控制实现**
  - [ ] 实现 `require_permission` 依赖注入/中间件
  - [ ] 全局 API 权限接入
  - [ ] 列表接口的资源过滤 (List Filtering)
- [ ] **权限管理界面**
  - [ ] API: 用户角色管理 (Grant/Revoke Role)
  - [ ] 前端：权限管理页面 (仅超管可见)

### 2.4 审计日志 (贯穿 Phase 2)
- [ ] **审计系统**
  - [ ] 定义 `AuditLog` 模型
  - [ ] 实现 `AuditService`
  - [ ] 在关键操作点埋点记录审计日志
  - [ ] API: 审计日志查询
  - [ ] 前端：审计日志查看器

---

## Phase 3: 优化与发布 (Optimization & Release) - Weeks 15-18

### 3.1 性能优化 (Week 15-16)
- [ ] **缓存策略**
  - [ ] 优化 Redis 缓存 (Minion Grains, User Info)
  - [ ] 实现 API 响应缓存
- [ ] **前端优化**
  - [ ] 启用 Next.js SSR/SSG 优化首屏
  - [ ] 优化大数据量列表渲染 (虚拟滚动)
- [ ] **数据库优化**
  - [ ] 添加必要的数据库索引
  - [ ] 优化复杂查询 SQL

### 3.2 可观测性与生产准备 (Week 17-18)
- [ ] **监控告警**
  - [ ] 集成 Prometheus 指标 (API Latency, Job Status)
  - [ ] 配置 Grafana 仪表盘
  - [ ] 配置健康检查端点 (Health Checks)
- [ ] **部署与文档**
  - [ ] 编写 Helm Charts / K8s Manifests
  - [ ] 完善 GitHub Actions CI/CD (构建, 推送镜像, 部署)
  - [ ] 编写用户手册和部署文档
  - [ ] 进行安全扫描和漏洞修复
