# SaltShark 技术实现方案 (Technical Specification)

**版本**: 1.0  
**日期**: 2025-11-27  
**状态**: 草案  
**作者**: 技术团队

**基于**: [PRD v1.7 - SaltShark 产品需求文档](./prd.prompt.md)

---

## 1. 技术架构

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         前端层                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Next.js 16 + React + TypeScript + shadcn/ui         │  │
│  │  - Dashboard 组件 (React Query 数据管理)              │  │
│  │  - Minion 管理组件 (Zustand 状态管理)                 │  │
│  │  - 远程执行组件 (实时 WebSocket)                      │  │
│  │  - Job 管理组件 (服务端渲染支持)                      │  │
│  │  - Auth.js + Keycloak 认证                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTPS/WebSocket
┌─────────────────────────────────────────────────────────────┐
│                       API 网关层                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  - 认证/授权中间件                                    │  │
│  │  - 请求路由                                           │  │
│  │  - 限流/熔断                                          │  │
│  │  - API 文档（OpenAPI/Swagger）                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  应用服务层 (FasterApp)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Minion      │  │  Execution   │  │  Job         │    │
│  │  Service     │  │  Service     │  │  Service     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Auth        │  │  Audit       │  │  Event       │    │
│  │  Service     │  │  Service     │  │  Service     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│  (TortoiseORM + PostgreSQL)                                │
└─────────────────────────────────────────────────────────────┘
        ↓                    ↓                    ↓
┌──────────────┐   ┌──────────────┐   �┌──────────────┐
│  Salt API    │   │  OpenFGA     │   │  PostgreSQL  │
│  (Salt       │   │  (权限)      │   │  (业务数据)  │
│   Master)    │   │              │   │              │
└──────────────┘   └──────────────┘   └──────────────┘
        ↓
┌──────────────────────────────────────────────┐
│             Salt Minions                      │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐         │
│  │Node1│  │Node2│  │Node3│  │...  │         │
│  └─────┘  └─────┘  └─────┘  └─────┘         │
└──────────────────────────────────────────────┘
         ↓ (获取用户信息)
┌──────────────────────────────────────────────┐
│      用户管理系统 API (自研)                  │
│  - 用户基本信息 (display_name, email)        │
│  - 组织架构信息 (department, team)           │
│  - 单用户查询: GET /users/{user_id}          │
│  - 批量查询: POST /users/batch               │
└──────────────────────────────────────────────┘
```

### 1.2 架构设计原则

1. **关注点分离**: 前后端分离，服务模块化
2. **无状态设计**: 后端服务无状态，便于水平扩展
3. **高可用**: 支持多实例部署，无单点故障
4. **安全优先**: 认证、授权、审计全覆盖
5. **可观测性**: 日志、指标、追踪完整

---

## 2. 技术栈选型

### 2.1 后端技术栈

| 组件 | 技术选型 | 版本 | 选型理由 |
|------|---------|------|---------|
| **编程语言** | Python | 3.11+ | 生态成熟、异步支持、Salt SDK 官方支持 |
| **Web 框架** | FasterApp | Latest | 基于 FastAPI 增强、高性能、异步原生 |
| **包管理器** | UV | Latest | 快速、现代化的 Python 包管理工具 |
| **ORM** | TortoiseORM | Latest | 原生异步、类 Django API、易用性高 |
| **数据库** | PostgreSQL | 15+ | 可靠性高、JSON 支持、性能优秀 |
| **缓存** | Redis | 7+ | 高性能、丰富数据结构、持久化支持 |
| **任务队列** | Celery | Latest | 成熟稳定、分布式任务调度 |
| **权限引擎** | OpenFGA | 1.5+ | Google Zanzibar 实现、细粒度权限 |
| **认证服务** | Keycloak | 23+ | 企业级 IAM、标准协议、功能完整 |
| **API 文档** | OpenAPI 3.1 | - | 自动生成、交互式测试、标准化 |

**技术选型说明**:

**FasterApp**:
- 基于 FastAPI 的增强框架，提供更多开箱即用功能
- 原生异步支持，性能优异
- 自动生成 OpenAPI 文档
- 类型提示支持，代码健壮性高

**TortoiseORM**:
- 原生异步 ORM，与 FastAPI 完美配合
- API 类似 Django ORM，学习成本低
- 支持 Pydantic 集成，数据验证便捷
- 自动迁移生成（Aerich）

**OpenFGA**:
- Google Zanzibar 论文的开源实现
- 支持复杂的关系型权限模型
- 毫秒级权限检查性能
- 灵活的 DSL 定义权限规则

### 2.2 前端技术栈

| 组件 | 技术选型 | 版本 | 选型理由 |
|------|---------|------|---------|
| **框架** | Next.js | 16 | SSR/SSG 支持、App Router、性能优化 |
| **语言** | TypeScript | Latest | 类型安全、开发体验好、重构友好 |
| **UI 库** | shadcn/ui | Latest | 无样式组件、可定制、高质量 |
| **CSS 框架** | TailwindCSS | Latest | 实用优先、开发效率高、体积小 |
| **状态管理** | Zustand | Latest | 轻量级、简单 API、无 Provider |
| **数据获取** | React Query | v5 | 缓存管理、自动重试、SSR 支持 |
| **认证** | Auth.js | v5 (NextAuth) | Next.js 深度集成、标准协议 |
| **实时通信** | Socket.IO Client | Latest | 双向通信、自动重连、广泛支持 |
| **表单管理** | React Hook Form | Latest | 性能优秀、验证灵活 |
| **代码规范** | ESLint + Prettier | Latest | 代码风格统一、质量保证 |

**技术选型说明**:

**Next.js 16 (App Router)**:
- 服务端渲染（SSR）优化首屏加载
- React Server Components 减少客户端 JS
- 内置图像和字体优化
- 流式渲染和 Suspense 支持

**shadcn/ui**:
- 基于 Radix UI 的无样式组件库
- 源码直接复制到项目，完全可控
- 与 TailwindCSS 深度集成
- 支持深色模式

**Zustand**:
- 体积小（< 1KB gzipped）
- 简洁的 API，无需 Context Provider
- 支持 Redux DevTools
- 服务端渲染友好

**React Query (TanStack Query v5)**:
- 强大的服务端状态管理
- 自动缓存、重试、轮询
- 乐观更新支持
- SSR/SSG 友好

### 2.3 DevOps 技术栈

| 组件 | 技术选型 | 版本 | 选型理由 |
|------|---------|------|---------|
| **容器** | Docker | 24+ | 标准化、隔离性、可移植 |
| **编排** | Kubernetes | 1.28+ | 云原生标准、自动扩缩容、高可用 |
| **包管理** | Helm | 3 | K8s 应用打包、版本管理、参数化 |
| **GitOps** | ArgoCD | Latest | 声明式部署、自动同步、回滚简单 |
| **CI/CD** | GitHub Actions | - | GitHub 原生、免费额度、易用 |
| **监控** | Prometheus + Grafana | Latest | 云原生标准、强大可视化 |
| **日志** | Loki + Promtail | Latest | 轻量级、与 Grafana 集成 |
| **追踪** | Jaeger | Latest (可选) | 分布式追踪、性能分析 |

---

## 3. 部署架构

### 3.1 生产环境部署

**目标环境**: 私有云 Kubernetes 集群

**规模要求**:
- Minion 数量: 1,000 - 10,000 台
- 并发用户: 100+ 运维人员
- 并发 Job: 50+ 任务同时执行
- Salt API QPS: 200+

**部署模式**:
- SaltShark Frontend: 3 副本（SSR 部署）
- SaltShark Backend: 3 副本（水平扩展）
- PostgreSQL: 主从复制（1 主 + 2 从）
- Redis: Sentinel 模式（1 主 + 2 从 + 3 哨兵）
- Salt Master: 3 节点 HA 集群

### 3.2 网络架构

**Salt Master 高可用集群**:

```
┌─────────────────────────────────────────────────────────┐
│           Kubernetes Cluster (私有云)                    │
│                                                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │         SaltShark Namespace                       │ │
│  │                                                   │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │ │
│  │  │ Frontend    │  │ Frontend    │  │ Frontend │ │ │
│  │  │ Pod 1       │  │ Pod 2       │  │ Pod 3    │ │ │
│  │  │ (Next.js)   │  │ (Next.js)   │  │(Next.js) │ │ │
│  │  └──────┬──────┘  └──────┬──────┘  └────┬─────┘ │ │
│  │         └─────────────────┴──────────────┘       │ │
│  │                           ↓                       │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │ │
│  │  │ Backend     │  │ Backend     │  │ Backend  │ │ │
│  │  │ Pod 1       │  │ Pod 2       │  │ Pod 3    │ │ │
│  │  │(FasterApp)  │  │(FasterApp)  │  │(FasterApp│ │ │
│  │  └──────┬──────┘  └──────┬──────┘  └────┬─────┘ │ │
│  │         └─────────────────┴──────────────┘       │ │
│  └───────────────────────────┼───────────────────────┘ │
│                              ↓                          │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Salt Master Cluster (StatefulSet)                │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────┐│ │
│  │  │Salt Master 1 │  │Salt Master 2 │  │ Master 3││ │
│  │  │  (Active)    │  │  (Standby)   │  │(Standby)││ │
│  │  └──────┬───────┘  └──────┬───────┘  └────┬────┘│ │
│  │         └─────────────────┴───────────────┘     │ │
│  │                           ↓                      │ │
│  │         共享存储 (PVC - NFS/CephFS)              │ │
│  └───────────────────────────────────────────────────┘ │
└──────────────────────────┼───────────────────────────────┘
                           ↓
        ┌──────────────────┴──────────────────┐
        ↓                                     ↓
  [Minion 集群 1]                      [Minion 集群 2]
  (1,000-5,000 nodes)                  (1,000-5,000 nodes)
```

**网络通信**:
- Frontend ↔ Backend: ClusterIP Service（集群内部通信）
- Backend ↔ Salt Master: Salt API (HTTPS)
- Salt Master ↔ Minions: ZeroMQ (4505/4506)
- Backend ↔ PostgreSQL: 内部 DNS
- Backend ↔ Redis: 内部 DNS
- Backend ↔ OpenFGA: 内部 DNS
- Backend ↔ 用户管理系统: HTTPS (Bearer Token)

### 3.3 资源规划

**SaltShark 组件资源配置**:

| 组件 | 副本数 | CPU Request | CPU Limit | Memory Request | Memory Limit |
|------|--------|-------------|-----------|----------------|--------------|
| Frontend (Next.js) | 3 | 500m | 2000m | 512Mi | 2Gi |
| Backend (FasterApp) | 3 | 500m | 2000m | 512Mi | 2Gi |
| PostgreSQL (主) | 1 | 2000m | 4000m | 4Gi | 8Gi |
| PostgreSQL (从) | 2 | 1000m | 2000m | 2Gi | 4Gi |
| Redis (主) | 1 | 500m | 1000m | 1Gi | 2Gi |
| Redis (从) | 2 | 500m | 1000m | 1Gi | 2Gi |
| OpenFGA | 2 | 500m | 1000m | 512Mi | 1Gi |

**总资源需求**:
- CPU: ~18-40 cores
- Memory: ~28-60 GB
- Storage: ~500 GB (数据库 + 审计日志)

**HPA 配置** (水平自动扩缩容):
- Backend: 3-10 副本（CPU 70%, Memory 80%）
- Frontend: 3-6 副本（CPU 70%）

---

## 4. 数据库设计

### 4.1 数据库选型

**PostgreSQL 15+**

选型理由:
- 成熟稳定，事务支持完善
- JSON/JSONB 类型，适合存储 Grains、Pillar 数据
- 丰富的索引类型（B-Tree、GIN、BRIN）
- 强大的查询优化器
- 主从复制、流复制支持高可用

### 4.2 数据模型设计

#### 4.2.1 用户引用表

**表名**: `user_references`

**用途**: 仅存储用户 ID 和活跃时间，不存储用户详细信息

**字段定义**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| user_id | VARCHAR(255) | PRIMARY KEY | 来自 Keycloak 的用户唯一标识 |
| first_seen | TIMESTAMP | NOT NULL, DEFAULT NOW() | 首次登录时间 |
| last_active | TIMESTAMP | NOT NULL, DEFAULT NOW() | 最后活跃时间 |

**索引**:
```sql
CREATE INDEX idx_user_last_active ON user_references(last_active);
```

**TortoiseORM 模型**:
```python
from tortoise import fields
from tortoise.models import Model

class UserReference(Model):
    """用户引用模型（仅存储用户ID和活跃时间）"""
    user_id = fields.CharField(max_length=255, pk=True)
    first_seen = fields.DatetimeField(auto_now_add=True)
    last_active = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "user_references"
```

**注意**: 用户的 display_name、email、department 等信息通过用户管理系统 API 实时获取，不在本地存储。

#### 4.2.2 Minion 元数据表

**表名**: `minions`

**用途**: 存储 Minion 的元数据和缓存的 Grains 信息

**字段定义**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | VARCHAR(255) | PRIMARY KEY | Minion ID（唯一标识符）|
| hostname | VARCHAR(255) | NULL | 主机名 |
| ip_address | INET | NULL | IP 地址（IPv4/IPv6）|
| os | VARCHAR(100) | NULL | 操作系统类型 |
| os_version | VARCHAR(100) | NULL | 操作系统版本 |
| last_seen | TIMESTAMP | NULL | 最后在线时间 |
| status | VARCHAR(50) | NOT NULL | 状态: online/offline/unaccepted |
| grains | JSONB | NULL | Grains 数据（JSON 格式）|
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 更新时间 |

**索引**:
```sql
CREATE INDEX idx_minions_status ON minions(status);
CREATE INDEX idx_minions_last_seen ON minions(last_seen);
CREATE INDEX idx_minions_hostname ON minions(hostname);
CREATE INDEX idx_minions_grains ON minions USING GIN(grains);
```

**TortoiseORM 模型**:
```python
class Minion(Model):
    """Minion 元数据模型"""
    id = fields.CharField(max_length=255, pk=True)
    hostname = fields.CharField(max_length=255, null=True)
    ip_address = fields.CharField(max_length=45, null=True)
    os = fields.CharField(max_length=100, null=True)
    os_version = fields.CharField(max_length=100, null=True)
    last_seen = fields.DatetimeField(null=True)
    status = fields.CharField(max_length=50)
    grains = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "minions"
```

#### 4.2.3 Job 历史表

**表名**: `jobs`

**用途**: 记录所有执行的 Job 及其结果

**字段定义**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| jid | VARCHAR(255) | PRIMARY KEY | Job ID（Salt 生成）|
| user_id | VARCHAR(255) | FK → user_references | 执行用户 |
| function | VARCHAR(255) | NOT NULL | Salt 函数名 |
| arguments | JSONB | NULL | 函数参数 |
| target | TEXT | NOT NULL | 目标表达式 |
| target_type | VARCHAR(50) | NOT NULL | 目标类型: glob/grain/pillar/compound |
| status | VARCHAR(50) | NOT NULL | 状态: running/success/failed |
| started_at | TIMESTAMP | NULL | 开始时间 |
| completed_at | TIMESTAMP | NULL | 完成时间 |
| result | JSONB | NULL | 执行结果 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |

**索引**:
```sql
CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_started_at ON jobs(started_at DESC);
CREATE INDEX idx_jobs_function ON jobs(function);
```

**TortoiseORM 模型**:
```python
class Job(Model):
    """Job 历史模型"""
    jid = fields.CharField(max_length=255, pk=True)
    user = fields.ForeignKeyField("models.UserReference", related_name="jobs")
    function = fields.CharField(max_length=255)
    arguments = fields.JSONField(null=True)
    target = fields.TextField()
    target_type = fields.CharField(max_length=50)
    status = fields.CharField(max_length=50)
    started_at = fields.DatetimeField(null=True)
    completed_at = fields.DatetimeField(null=True)
    result = fields.JSONField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "jobs"
```

#### 4.2.4 审计日志表

**表名**: `audit_logs`

**用途**: 记录所有用户操作，满足审计需求

**字段定义**:

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | BIGSERIAL | PRIMARY KEY | 自增主键 |
| timestamp | TIMESTAMP | NOT NULL, DEFAULT NOW() | 操作时间 |
| user_id | VARCHAR(255) | FK → user_references | 操作用户 |
| action | VARCHAR(100) | NOT NULL | 操作类型 |
| resource_type | VARCHAR(50) | NOT NULL | 资源类型: minion/job/permission |
| resource_id | VARCHAR(255) | NOT NULL | 资源 ID |
| parameters | JSONB | NULL | 操作参数 |
| result | VARCHAR(50) | NOT NULL | 结果: success/failure |
| ip_address | INET | NOT NULL | 客户端 IP |
| user_agent | TEXT | NULL | User Agent |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |

**索引**:
```sql
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
```

**TortoiseORM 模型**:
```python
class AuditLog(Model):
    """审计日志模型"""
    id = fields.BigIntField(pk=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    user = fields.ForeignKeyField("models.UserReference", related_name="audit_logs")
    action = fields.CharField(max_length=100)
    resource_type = fields.CharField(max_length=50)
    resource_id = fields.CharField(max_length=255)
    parameters = fields.JSONField(null=True)
    result = fields.CharField(max_length=50)
    ip_address = fields.CharField(max_length=45)
    user_agent = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "audit_logs"
```

### 4.3 数据库迁移

**工具**: Aerich (TortoiseORM 官方迁移工具)

**迁移流程**:
```bash
# 初始化 Aerich
aerich init -t app.db.TORTOISE_ORM

# 生成迁移文件
aerich migrate --name "init"

# 应用迁移
aerich upgrade

# 回滚迁移
aerich downgrade
```

**迁移最佳实践**:
1. 每次 schema 变更必须生成迁移文件
2. 迁移文件提交到 Git，确保可追溯
3. 生产环境应用前，先在测试环境验证
4. 大表变更使用在线 DDL 工具（如 gh-ost）

---

## 5. 权限系统设计

### 5.1 OpenFGA 权限模型

**模型定义语言**: OpenFGA DSL (schema 1.1)

#### 5.1.1 完整权限模型

```openfga
model
  schema 1.1

# 用户类型
type user

# 系统类型（单租户权限容器）
type system
  relations
    # 预设角色
    define super_admin: [user]
    define operator: [user]
    define viewer: [user]
    
    # 派生权限
    define can_manage_permissions: super_admin
    define can_manage_users: super_admin
    define can_view_audit_logs: super_admin or operator

# Minion 资源类型
type minion
  relations
    # 查看权限：所有角色
    define viewer: [user, system#viewer, system#operator, system#super_admin]
    
    # 操作权限：运维人员和超管
    define operator: [user, system#operator, system#super_admin]
    
    # 管理权限：仅超管（接受/删除 Key）
    define admin: [user, system#super_admin]

# Job 资源类型
type job
  relations
    # 查看 Job 信息
    define viewer: [user, system#viewer, system#operator, system#super_admin]
    
    # 执行 Job
    define executor: [user, system#operator, system#super_admin]
    
    # 终止 Job
    define terminator: [user, system#operator, system#super_admin]

# 权限管理资源类型
type permission_management
  relations
    # 权限管理能力：仅超管
    define manager: [user, system#super_admin]
```

#### 5.1.2 权限关系示例

**初始化超级管理员**:
```python
{
  "user": "user:admin@example.com",
  "relation": "super_admin",
  "object": "system:default"
}
```

**分配运维人员角色**:
```python
{
  "user": "user:operator1@example.com",
  "relation": "operator",
  "object": "system:default"
}
```

**分配只读用户角色**:
```python
{
  "user": "user:viewer1@example.com",
  "relation": "viewer",
  "object": "system:default"
}
```

#### 5.1.3 权限检查实现

**Python SDK 封装**:

```python
from openfga_sdk import OpenFgaClient, ClientConfiguration
from typing import Optional

class PermissionService:
    """权限服务封装"""
    
    def __init__(self, api_url: str, store_id: str, model_id: str):
        config = ClientConfiguration(
            api_url=api_url,
            store_id=store_id,
            authorization_model_id=model_id
        )
        self.client = OpenFgaClient(config)
    
    async def check_permission(
        self,
        user_id: str,
        relation: str,
        object_type: str,
        object_id: str = "*"
    ) -> bool:
        """检查用户是否有特定权限"""
        try:
            response = await self.client.check(
                user=f"user:{user_id}",
                relation=relation,
                object=f"{object_type}:{object_id}"
            )
            return response.allowed
        except Exception as e:
            logger.error(f"权限检查失败: {e}")
            return False
    
    async def is_super_admin(self, user_id: str) -> bool:
        """检查是否是超级管理员"""
        return await self.check_permission(
            user_id=user_id,
            relation="super_admin",
            object_type="system",
            object_id="default"
        )
    
    async def is_operator(self, user_id: str) -> bool:
        """检查是否是运维人员"""
        return await self.check_permission(
            user_id=user_id,
            relation="operator",
            object_type="system",
            object_id="default"
        )
    
    async def is_viewer(self, user_id: str) -> bool:
        """检查是否是只读用户"""
        return await self.check_permission(
            user_id=user_id,
            relation="viewer",
            object_type="system",
            object_id="default"
        )
    
    async def can_execute_on_minion(
        self,
        user_id: str,
        minion_id: str
    ) -> bool:
        """检查是否可以在 Minion 上执行命令"""
        return await self.check_permission(
            user_id=user_id,
            relation="operator",
            object_type="minion",
            object_id=minion_id
        )
    
    async def can_manage_permissions(self, user_id: str) -> bool:
        """检查是否可以管理权限"""
        return await self.check_permission(
            user_id=user_id,
            relation="manager",
            object_type="permission_management",
            object_id="default"
        )
    
    async def assign_role(
        self,
        user_id: str,
        role: str
    ) -> bool:
        """分配角色给用户"""
        try:
            await self.client.write([{
                "user": f"user:{user_id}",
                "relation": role,
                "object": "system:default"
            }])
            return True
        except Exception as e:
            logger.error(f"角色分配失败: {e}")
            return False
    
    async def revoke_role(
        self,
        user_id: str,
        role: str
    ) -> bool:
        """撤销用户的角色"""
        try:
            await self.client.delete([{
                "user": f"user:{user_id}",
                "relation": role,
                "object": "system:default"
            }])
            return True
        except Exception as e:
            logger.error(f"角色撤销失败: {e}")
            return False
    
    async def get_user_role(self, user_id: str) -> Optional[str]:
        """获取用户的角色"""
        if await self.is_super_admin(user_id):
            return "super_admin"
        elif await self.is_operator(user_id):
            return "operator"
        elif await self.is_viewer(user_id):
            return "viewer"
        return None
```

### 5.2 权限初始化

**配置文件**: `config/permissions.yaml`

```yaml
initial_setup:
  # 首个超级管理员的 user_id (来自 Keycloak)
  super_admin_user_id: "admin@example.com"
  
  # 可选：多个初始超管
  additional_super_admins:
    - "admin1@example.com"
    - "admin2@example.com"
```

**初始化脚本**:

```python
import yaml
from pathlib import Path
from app.services.permission import PermissionService
from app.models import SystemConfig

class PermissionInitializer:
    """权限系统初始化器"""
    
    def __init__(
        self,
        permission_service: PermissionService,
        config_path: str = "config/permissions.yaml"
    ):
        self.permission_service = permission_service
        self.config = self._load_config(config_path)
    
    def _load_config(self, path: str) -> dict:
        """加载权限配置文件"""
        config_file = Path(path)
        if not config_file.exists():
            raise FileNotFoundError(f"权限配置文件不存在: {path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    async def initialize_permissions(self):
        """初始化权限系统"""
        # 1. 检查是否已初始化
        if await self._is_initialized():
            logger.info("权限系统已初始化，跳过")
            return
        
        logger.info("开始初始化权限系统...")
        
        # 2. 创建授权模型
        await self._create_authorization_model()
        
        # 3. 设置首个超级管理员
        await self._setup_initial_super_admin()
        
        # 4. 标记为已初始化
        await self._mark_as_initialized()
        
        logger.info("权限系统初始化完成")
    
    async def _create_authorization_model(self):
        """创建 OpenFGA 授权模型"""
        # 读取模型定义文件
        model_path = Path("config/openfga_model.json")
        with open(model_path, 'r') as f:
            model = json.load(f)
        
        # 创建模型
        await self.permission_service.client.write_authorization_model(model)
        logger.info("OpenFGA 授权模型创建成功")
    
    async def _setup_initial_super_admin(self):
        """设置首个超级管理员"""
        admin_user_id = self.config["initial_setup"]["super_admin_user_id"]
        
        # 分配超管角色
        success = await self.permission_service.assign_role(
            user_id=admin_user_id,
            role="super_admin"
        )
        
        if success:
            logger.info(f"已设置初始超级管理员: {admin_user_id}")
        else:
            raise Exception(f"设置初始超级管理员失败: {admin_user_id}")
        
        # 设置额外的超管
        additional_admins = self.config["initial_setup"].get(
            "additional_super_admins", []
        )
        for admin_id in additional_admins:
            await self.permission_service.assign_role(
                user_id=admin_id,
                role="super_admin"
            )
            logger.info(f"已设置额外超级管理员: {admin_id}")
    
    async def _is_initialized(self) -> bool:
        """检查权限系统是否已初始化"""
        return await SystemConfig.filter(
            key="permissions_initialized"
        ).exists()
    
    async def _mark_as_initialized(self):
        """标记权限系统已初始化"""
        await SystemConfig.create(
            key="permissions_initialized",
            value="true"
        )
```

**应用启动时调用**:

```python
# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.services.permission import PermissionService
from app.core.permission_initializer import PermissionInitializer

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("应用启动中...")
    
    # 初始化数据库
    await init_db()
    
    # 初始化权限系统
    permission_service = PermissionService(
        api_url=settings.OPENFGA_API_URL,
        store_id=settings.OPENFGA_STORE_ID,
        model_id=settings.OPENFGA_MODEL_ID
    )
    
    initializer = PermissionInitializer(permission_service)
    await initializer.initialize_permissions()
    
    yield
    
    # 关闭时执行
    logger.info("应用关闭中...")
    await close_db()

app = FastAPI(lifespan=lifespan)
```

### 5.3 权限中间件

**FastAPI 依赖注入实现**:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.permission import PermissionService
from app.core.auth import get_current_user

security = HTTPBearer()

async def require_permission(
    required_relation: str,
    resource_type: str,
    resource_id: str = "*"
):
    """权限检查依赖"""
    async def permission_checker(
        current_user=Depends(get_current_user),
        permission_service=Depends(get_permission_service)
    ):
        has_permission = await permission_service.check_permission(
            user_id=current_user.user_id,
            relation=required_relation,
            object_type=resource_type,
            object_id=resource_id
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要 {required_relation} 权限"
            )
        
        return current_user
    
    return permission_checker

# 使用示例
@router.post("/minions/{minion_id}/execute")
async def execute_command(
    minion_id: str,
    command: CommandRequest,
    current_user=Depends(require_permission(
        required_relation="operator",
        resource_type="minion",
        resource_id=minion_id
    ))
):
    """在 Minion 上执行命令"""
    # 执行命令逻辑
    pass
```

**简化版依赖**:

```python
async def require_super_admin(
    current_user=Depends(get_current_user),
    permission_service=Depends(get_permission_service)
):
    """要求超级管理员权限"""
    if not await permission_service.is_super_admin(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限"
        )
    return current_user

async def require_operator(
    current_user=Depends(get_current_user),
    permission_service=Depends(get_permission_service)
):
    """要求运维人员权限"""
    if not await permission_service.is_operator(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要运维人员权限"
        )
    return current_user
```

---

## 6. 用户系统集成

### 6.1 集成架构

**设计原则**: SaltShark 不实现用户管理，所有用户信息从外部系统获取

```
┌──────────────┐
│  Keycloak    │  ← 认证：获取 user_id
│  (SSO/OIDC)  │
└──────┬───────┘
       │ JWT Token (含 user_id)
       ↓
┌──────────────┐
│  SaltShark   │
│   Backend    │
└──┬────┬────┬─┘
   │    │    │
   │    │    └──→ OpenFGA: 权限检查（使用 user_id）
   │    │
   │    └───────→ 本地数据库: 存储 user_id + 活跃时间
   │
   └────────────→ 用户管理系统 API: 获取用户详细信息
                  (display_name, email, department)
```

### 6.2 用户管理系统 API 客户端

**API 约定**:

| 接口 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 获取单个用户 | GET | `/api/v1/users/{user_id}` | 获取用户详细信息 |
| 批量获取用户 | POST | `/api/v1/users/batch` | 批量获取多个用户 |

**响应格式**:

```json
// GET /api/v1/users/{user_id}
{
  "user_id": "123456",
  "username": "zhangsan",
  "display_name": "张三",
  "email": "zhangsan@example.com",
  "department": "运维部",
  "phone": "13800138000",
  "avatar_url": "https://cdn.example.com/avatars/123456.jpg"
}

// POST /api/v1/users/batch
// Request Body: {"user_ids": ["123456", "234567"]}
{
  "123456": {
    "user_id": "123456",
    "username": "zhangsan",
    "display_name": "张三",
    "email": "zhangsan@example.com",
    "department": "运维部"
  },
  "234567": {
    "user_id": "234567",
    "username": "lisi",
    "display_name": "李四",
    "email": "lisi@example.com",
    "department": "开发部"
  }
}
```

**Python 客户端实现**:

```python
import httpx
from typing import Dict, List, Optional
from pydantic import BaseModel
from functools import lru_cache

class UserInfo(BaseModel):
    """用户信息模型"""
    user_id: str
    username: str
    display_name: str
    email: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None

class UserManagementClient:
    """用户管理系统 API 客户端"""
    
    def __init__(self, api_url: str, api_key: str, timeout: float = 30.0):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout
        )
    
    async def get_user_info(self, user_id: str) -> Optional[UserInfo]:
        """获取单个用户信息"""
        try:
            response = await self.client.get(
                f"{self.api_url}/api/v1/users/{user_id}"
            )
            response.raise_for_status()
            data = response.json()
            return UserInfo(**data)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"用户不存在: {user_id}")
                return None
            logger.error(f"获取用户信息失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取用户信息异常: {e}")
            raise
    
    async def get_users_batch(
        self,
        user_ids: List[str]
    ) -> Dict[str, UserInfo]:
        """批量获取用户信息"""
        if not user_ids:
            return {}
        
        try:
            response = await self.client.post(
                f"{self.api_url}/api/v1/users/batch",
                json={"user_ids": user_ids}
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                user_id: UserInfo(**user_data)
                for user_id, user_data in data.items()
            }
        except Exception as e:
            logger.error(f"批量获取用户信息失败: {e}")
            raise
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
```

### 6.3 用户信息缓存服务

**缓存策略**: Redis 缓存，TTL 5 分钟

```python
import json
from typing import Dict, List, Optional
from redis.asyncio import Redis
from app.clients.user_management import UserManagementClient, UserInfo

class UserInfoService:
    """用户信息服务（带缓存）"""
    
    CACHE_TTL = 300  # 5 分钟
    CACHE_PREFIX = "user_info:"
    
    def __init__(
        self,
        user_mgmt_client: UserManagementClient,
        redis_client: Redis
    ):
        self.user_mgmt_client = user_mgmt_client
        self.redis = redis_client
    
    async def get_user_info(self, user_id: str) -> Optional[UserInfo]:
        """获取用户信息（带缓存）"""
        # 1. 检查 Redis 缓存
        cache_key = f"{self.CACHE_PREFIX}{user_id}"
        cached = await self.redis.get(cache_key)
        
        if cached:
            try:
                data = json.loads(cached)
                return UserInfo(**data)
            except Exception as e:
                logger.warning(f"缓存数据解析失败: {e}")
        
        # 2. 从用户管理系统获取
        user_info = await self.user_mgmt_client.get_user_info(user_id)
        
        if user_info:
            # 3. 写入缓存
            await self.redis.setex(
                cache_key,
                self.CACHE_TTL,
                user_info.json()
            )
        
        return user_info
    
    async def get_users_batch(
        self,
        user_ids: List[str]
    ) -> Dict[str, UserInfo]:
        """批量获取用户信息（带缓存）"""
        if not user_ids:
            return {}
        
        result = {}
        missing_user_ids = []
        
        # 1. 批量检查缓存
        cache_keys = [f"{self.CACHE_PREFIX}{uid}" for uid in user_ids]
        cached_values = await self.redis.mget(cache_keys)
        
        for user_id, cached in zip(user_ids, cached_values):
            if cached:
                try:
                    data = json.loads(cached)
                    result[user_id] = UserInfo(**data)
                except Exception as e:
                    logger.warning(f"缓存数据解析失败: {e}")
                    missing_user_ids.append(user_id)
            else:
                missing_user_ids.append(user_id)
        
        # 2. 批量获取未缓存的用户
        if missing_user_ids:
            users = await self.user_mgmt_client.get_users_batch(
                missing_user_ids
            )
            
            # 3. 写入缓存
            pipeline = self.redis.pipeline()
            for user_id, user_info in users.items():
                cache_key = f"{self.CACHE_PREFIX}{user_id}"
                pipeline.setex(cache_key, self.CACHE_TTL, user_info.json())
                result[user_id] = user_info
            
            await pipeline.execute()
        
        return result
    
    async def invalidate_cache(self, user_id: str):
        """使缓存失效"""
        cache_key = f"{self.CACHE_PREFIX}{user_id}"
        await self.redis.delete(cache_key)
```

### 6.4 用户信息降级策略

**降级场景**: 用户管理系统 API 不可用时

**降级方案**:
1. 返回缓存数据（即使过期）
2. 如果缓存也不可用，返回 user_id 作为 display_name
3. 记录降级事件，发送告警

```python
async def get_user_info_with_fallback(
    self,
    user_id: str
) -> UserInfo:
    """获取用户信息（带降级）"""
    try:
        # 尝试正常获取
        user_info = await self.get_user_info(user_id)
        if user_info:
            return user_info
    except Exception as e:
        logger.error(f"获取用户信息失败，尝试降级: {e}")
    
    # 降级策略 1: 返回过期缓存
    cache_key = f"{self.CACHE_PREFIX}{user_id}"
    cached = await self.redis.get(cache_key)
    if cached:
        try:
            data = json.loads(cached)
            user_info = UserInfo(**data)
            logger.warning(f"使用过期缓存: {user_id}")
            return user_info
        except:
            pass
    
    # 降级策略 2: 返回最小信息
    logger.error(f"用户信息完全不可用，使用降级数据: {user_id}")
    return UserInfo(
        user_id=user_id,
        username=user_id,
        display_name=f"用户 {user_id[:8]}...",
        email=None,
        department="未知"
    )
```

---

## 7. Salt API 集成

### 7.1 Salt Master 配置

#### 7.1.1 Salt API 配置

**文件**: `/etc/salt/master.d/api.conf`

```yaml
rest_cherrypy:
  port: 8000
  host: 0.0.0.0
  ssl_crt: /etc/pki/tls/certs/salt-api.crt
  ssl_key: /etc/pki/tls/certs/salt-api.key
  webhook_disable_auth: False
```

#### 7.1.2 External Auth 配置

**文件**: `/etc/salt/master.d/external_auth.conf`

```yaml
external_auth:
  pam:
    saltshark:
      - '.*'         # 所有模块
      - '@wheel'     # Wheel 模块
      - '@runner'    # Runner 模块
      - '@jobs'      # Job 管理
```

**创建 SaltShark 专用账号**:

```bash
# 创建系统用户
sudo useradd -r -s /sbin/nologin saltshark

# 设置密码
echo "saltshark:$(openssl rand -base64 32)" | sudo chpasswd

# 添加 PAM 配置
sudo tee /etc/pam.d/salt-api <<EOF
auth    required    pam_unix.so
account required    pam_unix.so
EOF
```

### 7.2 Salt API 客户端

**Python 客户端实现**:

```python
import httpx
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

class SaltAPIClient:
    """Salt API 客户端"""
    
    def __init__(
        self,
        api_url: str,
        username: str,
        password: str,
        verify_ssl: bool = True,
        timeout: float = 30.0
    ):
        self.api_url = api_url.rstrip('/')
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.token: Optional[str] = None
        self.client = httpx.AsyncClient(
            verify=verify_ssl,
            timeout=timeout
        )
    
    async def login(self) -> bool:
        """登录获取 Token"""
        try:
            response = await self.client.post(
                f"{self.api_url}/login",
                json={
                    "username": self.username,
                    "password": self.password,
                    "eauth": "pam"
                }
            )
            response.raise_for_status()
            data = response.json()
            self.token = data["return"][0]["token"]
            logger.info("Salt API 登录成功")
            return True
        except Exception as e:
            logger.error(f"Salt API 登录失败: {e}")
            return False
    
    async def _ensure_authenticated(self):
        """确保已认证"""
        if not self.token:
            await self.login()
    
    async def execute_command(
        self,
        target: str,
        function: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        target_type: str = "glob"
    ) -> Dict:
        """执行命令"""
        await self._ensure_authenticated()
        
        payload = {
            "client": "local",
            "tgt": target,
            "fun": function,
            "tgt_type": target_type
        }
        
        if args:
            payload["arg"] = args
        if kwargs:
            payload["kwarg"] = kwargs
        
        try:
            response = await self.client.post(
                f"{self.api_url}/",
                json=[payload],
                headers={"X-Auth-Token": self.token}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"命令执行失败: {e}")
            raise
    
    async def list_minions(self) -> List[str]:
        """获取所有 Minion 列表"""
        await self._ensure_authenticated()
        
        try:
            response = await self.client.get(
                f"{self.api_url}/minions",
                headers={"X-Auth-Token": self.token}
            )
            response.raise_for_status()
            data = response.json()
            return list(data["return"][0].keys())
        except Exception as e:
            logger.error(f"获取 Minion 列表失败: {e}")
            raise
    
    async def get_minion_grains(self, minion_id: str) -> Dict:
        """获取 Minion 的 Grains"""
        result = await self.execute_command(
            target=minion_id,
            function="grains.items"
        )
        return result["return"][0].get(minion_id, {})
    
    async def accept_key(self, minion_id: str) -> bool:
        """接受 Minion Key"""
        await self._ensure_authenticated()
        
        try:
            response = await self.client.post(
                f"{self.api_url}/keys",
                json={
                    "mid": minion_id,
                    "act": "accept"
                },
                headers={"X-Auth-Token": self.token}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"接受 Key 失败: {e}")
            return False
    
    async def delete_key(self, minion_id: str) -> bool:
        """删除 Minion Key"""
        await self._ensure_authenticated()
        
        try:
            response = await self.client.delete(
                f"{self.api_url}/keys/{minion_id}",
                headers={"X-Auth-Token": self.token}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"删除 Key 失败: {e}")
            return False
    
    async def get_job_status(self, jid: str) -> Dict:
        """获取 Job 状态"""
        await self._ensure_authenticated()
        
        try:
            response = await self.client.get(
                f"{self.api_url}/jobs/{jid}",
                headers={"X-Auth-Token": self.token}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"获取 Job 状态失败: {e}")
            raise
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
```

### 7.3 Salt Event Bus 集成

**WebSocket 事件监听**:

```python
import asyncio
import websockets
import json
from typing import Callable, Dict

class SaltEventListener:
    """Salt Event Bus 监听器"""
    
    def __init__(
        self,
        websocket_url: str,
        token: str
    ):
        self.websocket_url = websocket_url
        self.token = token
        self.handlers: Dict[str, Callable] = {}
        self.running = False
    
    def on_event(self, tag: str):
        """注册事件处理器"""
        def decorator(func: Callable):
            self.handlers[tag] = func
            return func
        return decorator
    
    async def start(self):
        """启动事件监听"""
        self.running = True
        
        async with websockets.connect(
            f"{self.websocket_url}/ws/{self.token}"
        ) as websocket:
            logger.info("已连接到 Salt Event Bus")
            
            while self.running:
                try:
                    message = await websocket.recv()
                    event = json.loads(message)
                    
                    tag = event.get("tag", "")
                    data = event.get("data", {})
                    
                    # 调用匹配的处理器
                    for pattern, handler in self.handlers.items():
                        if tag.startswith(pattern):
                            await handler(tag, data)
                
                except websockets.ConnectionClosed:
                    logger.warning("WebSocket 连接断开，尝试重连...")
                    await asyncio.sleep(5)
                    break
                except Exception as e:
                    logger.error(f"处理事件失败: {e}")
    
    async def stop(self):
        """停止事件监听"""
        self.running = False

# 使用示例
event_listener = SaltEventListener(
    websocket_url="wss://salt-master:8000",
    token=salt_api_token
)

@event_listener.on_event("salt/job/")
async def handle_job_event(tag: str, data: dict):
    """处理 Job 事件"""
    jid = data.get("jid")
    logger.info(f"Job 事件: {jid}")
    
    # 更新数据库中的 Job 状态
    await update_job_status(jid, data)

# 启动监听
asyncio.create_task(event_listener.start())
```

---

## 8. 开发环境

### 8.1 Docker Compose 开发环境

**文件**: `docker-compose.dev.yml`

```yaml
version: '3.8'

services:
  # Salt Master (单节点开发环境)
  salt-master:
    image: saltstack/salt:latest
    container_name: salt-master-dev
    ports:
      - "4505:4505"  # Publisher
      - "4506:4506"  # Request Server
      - "8000:8000"  # Salt API
    volumes:
      - ./dev/salt/master.conf:/etc/salt/master
      - ./dev/salt/api.conf:/etc/salt/master.d/api.conf
      - ./dev/salt/external_auth.conf:/etc/salt/master.d/external_auth.conf
      - salt-pki:/etc/salt/pki
      - salt-cache:/var/cache/salt
    environment:
      - SALT_API_ENABLED=true
    networks:
      - saltshark-dev

  # Salt Minion (模拟受控节点)
  salt-minion-1:
    image: saltstack/salt:latest
    container_name: salt-minion-1
    depends_on:
      - salt-master
    volumes:
      - ./dev/salt/minion.conf:/etc/salt/minion
    environment:
      - SALT_MASTER=salt-master
    networks:
      - saltshark-dev

  # Keycloak (SSO)
  keycloak:
    image: quay.io/keycloak/keycloak:23.0
    container_name: keycloak-dev
    ports:
      - "8080:8080"
    environment:
      - KEYCLOAK_ADMIN=admin
      - KEYCLOAK_ADMIN_PASSWORD=admin
      - KC_DB=postgres
      - KC_DB_URL=jdbc:postgresql://postgres:5432/keycloak
      - KC_DB_USERNAME=keycloak
      - KC_DB_PASSWORD=keycloak
      - KC_HOSTNAME=localhost
      - KC_HTTP_ENABLED=true
    command: start-dev
    depends_on:
      - postgres
    networks:
      - saltshark-dev

  # PostgreSQL (主数据库)
  postgres:
    image: postgres:15-alpine
    container_name: postgres-dev
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=saltshark
      - POSTGRES_PASSWORD=saltshark
      - POSTGRES_DB=saltshark
      - POSTGRES_MULTIPLE_DATABASES=keycloak,openfga
    volumes:
      - ./dev/scripts/create-databases.sh:/docker-entrypoint-initdb.d/create-databases.sh
      - postgres-data:/var/lib/postgresql/data
    networks:
      - saltshark-dev

  # Redis (缓存和任务队列)
  redis:
    image: redis:7-alpine
    container_name: redis-dev
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    networks:
      - saltshark-dev

  # OpenFGA (权限管理)
  openfga:
    image: openfga/openfga:latest
    container_name: openfga-dev
    ports:
      - "8081:8080"
      - "8082:8081"  # gRPC
      - "3000:3000"  # Playground
    environment:
      - OPENFGA_DATASTORE_ENGINE=postgres
      - OPENFGA_DATASTORE_URI=postgres://saltshark:saltshark@postgres:5432/openfga?sslmode=disable
      - OPENFGA_LOG_LEVEL=info
    depends_on:
      - postgres
    networks:
      - saltshark-dev

  # 用户管理系统 Mock 服务 (开发环境)
  user-management-mock:
    image: mockserver/mockserver:latest
    container_name: user-mgmt-mock
    ports:
      - "9000:1080"
    environment:
      - MOCKSERVER_INITIALIZATION_JSON_PATH=/config/expectations.json
    volumes:
      - ./dev/mock/user-management-expectations.json:/config/expectations.json
    networks:
      - saltshark-dev

volumes:
  salt-pki:
  salt-cache:
  postgres-data:
  redis-data:

networks:
  saltshark-dev:
    driver: bridge
```

### 8.2 开发环境配置文件

**PostgreSQL 多数据库脚本**: `dev/scripts/create-databases.sh`

```bash
#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE keycloak;
    GRANT ALL PRIVILEGES ON DATABASE keycloak TO $POSTGRES_USER;
    
    CREATE DATABASE openfga;
    GRANT ALL PRIVILEGES ON DATABASE openfga TO $POSTGRES_USER;
EOSQL
```

**Salt Master 配置**: `dev/salt/master.conf`

```yaml
interface: 0.0.0.0
auto_accept: False
file_roots:
  base:
    - /srv/salt
pillar_roots:
  base:
    - /srv/pillar
```

**用户管理系统 Mock 期望**: `dev/mock/user-management-expectations.json`

```json
[
  {
    "httpRequest": {
      "method": "GET",
      "path": "/api/v1/users/.*"
    },
    "httpResponse": {
      "statusCode": 200,
      "body": {
        "user_id": "$1",
        "username": "test_user",
        "display_name": "测试用户",
        "email": "test@example.com",
        "department": "开发部"
      }
    }
  },
  {
    "httpRequest": {
      "method": "POST",
      "path": "/api/v1/users/batch"
    },
    "httpResponse": {
      "statusCode": 200,
      "body": {}
    }
  }
]
```

### 8.3 启动开发环境

```bash
# 启动所有服务
docker-compose -f docker-compose.dev.yml up -d

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f

# 停止所有服务
docker-compose -f docker-compose.dev.yml down

# 清理所有数据
docker-compose -f docker-compose.dev.yml down -v
```

### 8.4 本地开发

**后端开发**:

```bash
# 安装 UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt

# 运行数据库迁移
aerich upgrade

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**前端开发**:

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问 http://localhost:3000
```

---

现在继续添加 API 设计和前端实现部分：

## 9. API 设计

### 9.1 API 概览

**基础路径**: `/api/v1`

**认证**: 所有接口需要 JWT Bearer Token

**响应格式**:

```json
// 成功响应
{
  "code": 0,
  "data": { ... },
  "message": "success"
}

// 错误响应
{
  "code": 40001,
  "data": null,
  "message": "权限不足"
}
```

### 9.2 Minion 管理接口

#### 9.2.1 列表查询

```
GET /api/v1/minions
```

**Query Parameters**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| page_size | integer | 否 | 每页数量，默认 20，最大 100 |
| search | string | 否 | 搜索关键词（ID、IP、主机名） |
| status | string | 否 | 状态过滤：online, offline, unknown |
| tags | string | 否 | 标签过滤，逗号分隔 |
| sort_by | string | 否 | 排序字段：id, last_seen, created_at |
| sort_order | string | 否 | 排序方向：asc, desc |

**Response**:

```json
{
  "code": 0,
  "data": {
    "total": 150,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "minion_id": "web-server-01",
        "grains": {
          "os": "CentOS",
          "osversion": "7.9",
          "ip4": ["192.168.1.100"],
          "hostname": "web-01"
        },
        "status": "online",
        "last_seen": "2024-01-15T10:30:00Z",
        "created_at": "2024-01-01T08:00:00Z",
        "tags": ["web", "production"]
      }
    ]
  },
  "message": "success"
}
```

#### 9.2.2 获取单个 Minion

```
GET /api/v1/minions/{minion_id}
```

**Response**:

```json
{
  "code": 0,
  "data": {
    "minion_id": "web-server-01",
    "grains": { ... },
    "status": "online",
    "last_seen": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-01T08:00:00Z",
    "tags": ["web", "production"],
    "pillar": { ... },  // 如果有权限
    "recent_jobs": [    // 最近 10 个任务
      {
        "jid": "20240115103000123456",
        "function": "test.ping",
        "status": "completed",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ]
  },
  "message": "success"
}
```

#### 9.2.3 刷新 Minion 数据

```
POST /api/v1/minions/{minion_id}/refresh
```

**权限**: `minion:refresh`

**Description**: 从 Salt Master 重新拉取 Grains 数据

**Response**:

```json
{
  "code": 0,
  "data": {
    "minion_id": "web-server-01",
    "grains": { ... },  // 更新后的数据
    "updated_at": "2024-01-15T10:35:00Z"
  },
  "message": "刷新成功"
}
```

#### 9.2.4 批量接受 Key

```
POST /api/v1/minions/keys/accept
```

**权限**: `minion:accept_key`

**Request Body**:

```json
{
  "minion_ids": ["web-server-02", "web-server-03"]
}
```

**Response**:

```json
{
  "code": 0,
  "data": {
    "accepted": ["web-server-02", "web-server-03"],
    "failed": []
  },
  "message": "批量接受成功"
}
```

### 9.3 任务管理接口

#### 9.3.1 执行命令

```
POST /api/v1/jobs/execute
```

**权限**: `job:create` + `minion:execute` (目标 Minion)

**Request Body**:

```json
{
  "target": "web-*",           // 目标表达式
  "target_type": "glob",       // glob | list | grain | compound
  "function": "cmd.run",       // Salt 函数
  "args": ["ls -la /tmp"],     // 位置参数
  "kwargs": {                  // 关键字参数
    "timeout": 60
  },
  "async": true                // 是否异步执行
}
```

**Response** (异步执行):

```json
{
  "code": 0,
  "data": {
    "jid": "20240115103000123456",
    "target": "web-*",
    "function": "cmd.run",
    "created_at": "2024-01-15T10:30:00Z",
    "created_by": "123456",
    "status": "running",
    "minions": ["web-server-01", "web-server-02"]  // 匹配到的 Minion
  },
  "message": "任务已提交"
}
```

#### 9.3.2 获取任务结果

```
GET /api/v1/jobs/{jid}
```

**Response**:

```json
{
  "code": 0,
  "data": {
    "jid": "20240115103000123456",
    "target": "web-*",
    "function": "cmd.run",
    "created_at": "2024-01-15T10:30:00Z",
    "created_by": "123456",
    "created_by_name": "张三",
    "status": "completed",
    "result": {
      "web-server-01": {
        "success": true,
        "return": "total 24\ndrwxrwxrwt ...",
        "retcode": 0
      },
      "web-server-02": {
        "success": true,
        "return": "total 32\ndrwxrwxrwt ...",
        "retcode": 0
      }
    },
    "completed_at": "2024-01-15T10:30:15Z",
    "duration": 15.2
  },
  "message": "success"
}
```

#### 9.3.3 任务列表

```
GET /api/v1/jobs
```

**Query Parameters**: 同 Minion 列表

**Response**:

```json
{
  "code": 0,
  "data": {
    "total": 500,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "jid": "20240115103000123456",
        "target": "web-*",
        "function": "cmd.run",
        "created_at": "2024-01-15T10:30:00Z",
        "created_by": "123456",
        "created_by_name": "张三",
        "status": "completed",
        "success_count": 2,
        "failed_count": 0,
        "total_count": 2
      }
    ]
  },
  "message": "success"
}
```

### 9.4 权限检查接口

#### 9.4.1 检查权限

```
POST /api/v1/permissions/check
```

**Request Body**:

```json
{
  "user_id": "123456",
  "object_type": "minion",
  "object_id": "web-server-01",
  "relation": "execute"
}
```

**Response**:

```json
{
  "code": 0,
  "data": {
    "allowed": true
  },
  "message": "success"
}
```

#### 9.4.2 批量检查权限

```
POST /api/v1/permissions/check-batch
```

**Request Body**:

```json
{
  "user_id": "123456",
  "checks": [
    {
      "object_type": "minion",
      "object_id": "web-server-01",
      "relation": "execute"
    },
    {
      "object_type": "minion",
      "object_id": "db-server-01",
      "relation": "execute"
    }
  ]
}
```

**Response**:

```json
{
  "code": 0,
  "data": {
    "results": [
      {
        "object_type": "minion",
        "object_id": "web-server-01",
        "relation": "execute",
        "allowed": true
      },
      {
        "object_type": "minion",
        "object_id": "db-server-01",
        "relation": "execute",
        "allowed": false
      }
    ]
  },
  "message": "success"
}
```

### 9.5 审计日志接口

```
GET /api/v1/audit-logs
```

**Query Parameters**:

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码 |
| page_size | integer | 否 | 每页数量 |
| user_id | string | 否 | 用户ID过滤 |
| action | string | 否 | 操作类型过滤 |
| start_time | string | 否 | 开始时间 (ISO 8601) |
| end_time | string | 否 | 结束时间 (ISO 8601) |

**Response**:

```json
{
  "code": 0,
  "data": {
    "total": 1000,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "user_id": "123456",
        "user_name": "张三",
        "action": "minion.execute",
        "resource_type": "minion",
        "resource_id": "web-server-01",
        "details": {
          "function": "cmd.run",
          "args": ["ls -la"]
        },
        "ip_address": "192.168.1.50",
        "user_agent": "Mozilla/5.0 ...",
        "created_at": "2024-01-15T10:30:00Z"
      }
    ]
  },
  "message": "success"
}
```

---

## 10. 前端实现

### 10.1 技术栈详细配置

#### 10.1.1 Next.js 配置

**文件**: `next.config.mjs`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // React 严格模式
  reactStrictMode: true,
  
  // 输出模式：standalone 用于 Docker 部署
  output: 'standalone',
  
  // 环境变量
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_KEYCLOAK_URL: process.env.NEXT_PUBLIC_KEYCLOAK_URL,
    NEXT_PUBLIC_KEYCLOAK_REALM: process.env.NEXT_PUBLIC_KEYCLOAK_REALM,
    NEXT_PUBLIC_KEYCLOAK_CLIENT_ID: process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID,
  },
  
  // 图片优化
  images: {
    domains: ['cdn.example.com'],
  },
  
  // Webpack 配置
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': './src',
    };
    return config;
  },
};

export default nextConfig;
```

#### 10.1.2 TypeScript 配置

**文件**: `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

### 10.2 项目结构

```
frontend/
├── src/
│   ├── app/                    # Next.js 16 App Router
│   │   ├── (auth)/            # 认证路由组
│   │   │   ├── login/
│   │   │   └── callback/
│   │   ├── (dashboard)/       # 主界面路由组
│   │   │   ├── minions/
│   │   │   │   ├── page.tsx           # Minion 列表
│   │   │   │   └── [id]/page.tsx      # Minion 详情
│   │   │   ├── jobs/
│   │   │   │   ├── page.tsx           # Job 列表
│   │   │   │   ├── new/page.tsx       # 创建 Job
│   │   │   │   └── [jid]/page.tsx     # Job 详情
│   │   │   └── audit-logs/
│   │   │       └── page.tsx           # 审计日志
│   │   ├── layout.tsx         # 根布局
│   │   └── page.tsx           # 首页
│   ├── components/            # React 组件
│   │   ├── minions/
│   │   │   ├── MinionList.tsx
│   │   │   ├── MinionCard.tsx
│   │   │   └── MinionStatusBadge.tsx
│   │   ├── jobs/
│   │   │   ├── JobList.tsx
│   │   │   ├── JobExecuteForm.tsx
│   │   │   └── JobResultViewer.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Breadcrumb.tsx
│   │   └── ui/                # shadcn/ui 组件
│   │       ├── button.tsx
│   │       ├── input.tsx
│   │       ├── table.tsx
│   │       └── ...
│   ├── lib/                   # 工具库
│   │   ├── api/               # API 客户端
│   │   │   ├── client.ts      # Axios 封装
│   │   │   ├── minions.ts
│   │   │   ├── jobs.ts
│   │   │   └── auth.ts
│   │   ├── hooks/             # 自定义 Hooks
│   │   │   ├── useMinions.ts
│   │   │   ├── useJobs.ts
│   │   │   └── useAuth.ts
│   │   ├── store/             # Zustand 状态管理
│   │   │   ├── authStore.ts
│   │   │   └── uiStore.ts
│   │   └── utils/             # 工具函数
│   │       ├── cn.ts          # Tailwind className 合并
│   │       ├── format.ts
│   │       └── validators.ts
│   ├── types/                 # TypeScript 类型定义
│   │   ├── minion.ts
│   │   ├── job.ts
│   │   └── api.ts
│   └── middleware.ts          # Next.js 中间件
├── public/
├── .env.local
├── next.config.mjs
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

### 10.3 认证集成

#### 10.3.1 Auth.js (NextAuth v5) 配置

**文件**: `src/lib/auth.ts`

```typescript
import NextAuth from "next-auth";
import Keycloak from "next-auth/providers/keycloak";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Keycloak({
      clientId: process.env.KEYCLOAK_CLIENT_ID!,
      clientSecret: process.env.KEYCLOAK_CLIENT_SECRET!,
      issuer: `${process.env.KEYCLOAK_URL}/realms/${process.env.KEYCLOAK_REALM}`,
    }),
  ],
  callbacks: {
    async jwt({ token, account, profile }) {
      if (account && profile) {
        token.accessToken = account.access_token;
        token.userId = profile.sub;
      }
      return token;
    },
    async session({ session, token }) {
      if (token) {
        session.accessToken = token.accessToken as string;
        session.user.id = token.userId as string;
      }
      return session;
    },
  },
  pages: {
    signIn: "/login",
    signOut: "/logout",
    error: "/auth/error",
  },
});
```

**文件**: `src/app/api/auth/[...nextauth]/route.ts`

```typescript
import { handlers } from "@/lib/auth";

export const { GET, POST } = handlers;
```

#### 10.3.2 认证中间件

**文件**: `src/middleware.ts`

```typescript
import { auth } from "@/lib/auth";
import { NextResponse } from "next/server";

export default auth((req) => {
  const isLoggedIn = !!req.auth;
  const isAuthPage = req.nextUrl.pathname.startsWith("/login");

  // 未登录用户访问受保护页面 -> 重定向到登录
  if (!isLoggedIn && !isAuthPage) {
    return NextResponse.redirect(new URL("/login", req.url));
  }

  // 已登录用户访问登录页 -> 重定向到首页
  if (isLoggedIn && isAuthPage) {
    return NextResponse.redirect(new URL("/minions", req.url));
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

### 10.4 API 客户端

**文件**: `src/lib/api/client.ts`

```typescript
import axios, { AxiosInstance, AxiosError } from "axios";
import { getSession } from "next-auth/react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // 请求拦截器：添加 Token
    this.client.interceptors.request.use(
      async (config) => {
        const session = await getSession();
        if (session?.accessToken) {
          config.headers.Authorization = `Bearer ${session.accessToken}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 响应拦截器：统一错误处理
    this.client.interceptors.response.use(
      (response) => response.data,
      (error: AxiosError<ApiErrorResponse>) => {
        if (error.response) {
          const { code, message } = error.response.data;
          
          // 401: Token 过期或无效
          if (error.response.status === 401) {
            window.location.href = "/login";
          }
          
          // 403: 权限不足
          if (error.response.status === 403) {
            throw new Error("权限不足");
          }
          
          throw new Error(message || "请求失败");
        }
        
        throw new Error("网络错误");
      }
    );
  }

  public get instance() {
    return this.client;
  }
}

export const apiClient = new ApiClient().instance;

// 类型定义
interface ApiResponse<T = any> {
  code: number;
  data: T;
  message: string;
}

interface ApiErrorResponse {
  code: number;
  message: string;
}
```

**文件**: `src/lib/api/minions.ts`

```typescript
import { apiClient } from "./client";
import type { Minion, MinionListResponse, MinionFilters } from "@/types/minion";

export const minionApi = {
  // 获取 Minion 列表
  async getMinions(filters: MinionFilters): Promise<MinionListResponse> {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, String(value));
      }
    });
    
    return apiClient.get(`/api/v1/minions?${params.toString()}`);
  },

  // 获取单个 Minion
  async getMinion(minionId: string): Promise<Minion> {
    return apiClient.get(`/api/v1/minions/${minionId}`);
  },

  // 刷新 Minion 数据
  async refreshMinion(minionId: string): Promise<Minion> {
    return apiClient.post(`/api/v1/minions/${minionId}/refresh`);
  },

  // 批量接受 Key
  async acceptKeys(minionIds: string[]): Promise<{ accepted: string[]; failed: string[] }> {
    return apiClient.post("/api/v1/minions/keys/accept", { minion_ids: minionIds });
  },
};
```

### 10.5 React Query 集成

**文件**: `src/lib/hooks/useMinions.ts`

```typescript
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { minionApi } from "@/lib/api/minions";
import type { MinionFilters } from "@/types/minion";

export function useMinions(filters: MinionFilters) {
  return useQuery({
    queryKey: ["minions", filters],
    queryFn: () => minionApi.getMinions(filters),
    staleTime: 30000, // 30 秒
    refetchInterval: 60000, // 1 分钟自动刷新
  });
}

export function useMinion(minionId: string) {
  return useQuery({
    queryKey: ["minion", minionId],
    queryFn: () => minionApi.getMinion(minionId),
    enabled: !!minionId,
  });
}

export function useRefreshMinion() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (minionId: string) => minionApi.refreshMinion(minionId),
    onSuccess: (data, minionId) => {
      // 更新缓存
      queryClient.setQueryData(["minion", minionId], data);
      queryClient.invalidateQueries({ queryKey: ["minions"] });
    },
  });
}
```

### 10.6 Minion 列表组件

**文件**: `src/app/(dashboard)/minions/page.tsx`

```typescript
"use client";

import { useState } from "react";
import { useMinions } from "@/lib/hooks/useMinions";
import { MinionCard } from "@/components/minions/MinionCard";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { Loader2 } from "lucide-react";

export default function MinionsPage() {
  const [filters, setFilters] = useState({
    page: 1,
    page_size: 20,
    search: "",
    status: "",
  });

  const { data, isLoading, error } = useMinions(filters);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen text-red-500">
        加载失败: {error.message}
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Minion 管理</h1>
        <Button onClick={() => {/* 刷新 */}}>刷新</Button>
      </div>

      {/* 筛选器 */}
      <div className="flex gap-4 mb-6">
        <Input
          placeholder="搜索 Minion ID、IP、主机名..."
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value, page: 1 })}
          className="max-w-md"
        />
        <Select
          value={filters.status}
          onValueChange={(status) => setFilters({ ...filters, status, page: 1 })}
        >
          <option value="">全部状态</option>
          <option value="online">在线</option>
          <option value="offline">离线</option>
        </Select>
      </div>

      {/* Minion 列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {data?.data.items.map((minion) => (
          <MinionCard key={minion.minion_id} minion={minion} />
        ))}
      </div>

      {/* 分页 */}
      <div className="flex justify-center mt-6">
        <Button
          disabled={filters.page === 1}
          onClick={() => setFilters({ ...filters, page: filters.page - 1 })}
        >
          上一页
        </Button>
        <span className="mx-4">
          第 {filters.page} 页 / 共 {Math.ceil(data.data.total / filters.page_size)} 页
        </span>
        <Button
          disabled={filters.page * filters.page_size >= data.data.total}
          onClick={() => setFilters({ ...filters, page: filters.page + 1 })}
        >
          下一页
        </Button>
      </div>
    </div>
  );
}
```

---

继续添加部署和监控部分：

## 11. 部署方案

### 11.1 CI/CD 流程

**GitHub Actions 工作流**: `.github/workflows/deploy.yml`

```yaml
name: Build and Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME_BACKEND: ${{ github.repository }}/backend
  IMAGE_NAME_FRONTEND: ${{ github.repository }}/frontend

jobs:
  # 后端测试和构建
  backend:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      
      - name: 设置 Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: 安装 UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: 安装依赖
        run: |
          cd backend
          uv pip install -r requirements.txt
      
      - name: 运行测试
        run: |
          cd backend
          pytest --cov --cov-fail-under=80
      
      - name: 代码检查
        run: |
          cd backend
          ruff check .
          mypy .
      
      - name: 构建 Docker 镜像
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: ${{ github.event_name != 'pull_request' }}
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME_BACKEND }}:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME_BACKEND }}:latest
  
  # 前端测试和构建
  frontend:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      
      - name: 设置 Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: 安装依赖
        run: |
          cd frontend
          npm ci
      
      - name: 代码检查
        run: |
          cd frontend
          npm run lint
          npm run type-check
      
      - name: 构建
        run: |
          cd frontend
          npm run build
      
      - name: 构建 Docker 镜像
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          push: ${{ github.event_name != 'pull_request' }}
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME_FRONTEND }}:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME_FRONTEND }}:latest
  
  # 部署到 Kubernetes
  deploy:
    needs: [backend, frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
      
      - name: 安装 Helm
        uses: azure/setup-helm@v3
        with:
          version: '3.13.0'
      
      - name: 更新 Helm Chart
        run: |
          cd helm/saltshark
          sed -i "s/tag: .*/tag: ${{ github.sha }}/" values.yaml
      
      - name: 部署到 Kubernetes
        env:
          KUBECONFIG_DATA: ${{ secrets.KUBECONFIG }}
        run: |
          echo "$KUBECONFIG_DATA" | base64 -d > kubeconfig
          export KUBECONFIG=./kubeconfig
          helm upgrade --install saltshark ./helm/saltshark \
            --namespace saltshark \
            --create-namespace \
            --wait \
            --timeout 10m
```

### 11.2 Helm Chart 结构

```
helm/saltshark/
├── Chart.yaml
├── values.yaml
├── values-prod.yaml
├── values-staging.yaml
└── templates/
    ├── _helpers.tpl
    ├── backend-deployment.yaml
    ├── backend-service.yaml
    ├── backend-hpa.yaml
    ├── frontend-deployment.yaml
    ├── frontend-service.yaml
    ├── frontend-hpa.yaml
    ├── postgres-statefulset.yaml
    ├── postgres-service.yaml
    ├── redis-deployment.yaml
    ├── redis-service.yaml
    ├── openfga-deployment.yaml
    ├── openfga-service.yaml
    ├── celery-worker-deployment.yaml
    ├── celery-beat-deployment.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── secret.yaml
    └── pvc.yaml
```

**Chart.yaml**:

```yaml
apiVersion: v2
name: saltshark
description: SaltShark - Salt 管理平台
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - saltstack
  - devops
  - automation
maintainers:
  - name: SaltShark Team
    email: team@example.com
```

**values.yaml** (核心配置):

```yaml
# 全局配置
global:
  imageRegistry: ghcr.io
  imagePullSecrets:
    - name: ghcr-secret

# 后端配置
backend:
  replicaCount: 3
  image:
    repository: ghcr.io/example/saltshark/backend
    tag: latest
    pullPolicy: IfNotPresent
  
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi
  
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
  
  env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: saltshark-secrets
          key: database-url
    - name: REDIS_URL
      value: "redis://saltshark-redis:6379/0"
    - name: OPENFGA_API_URL
      value: "http://saltshark-openfga:8080"
    - name: SALT_API_URL
      valueFrom:
        configMapKeyRef:
          name: saltshark-config
          key: salt-api-url
  
  livenessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 30
    periodSeconds: 10
  
  readinessProbe:
    httpGet:
      path: /health/ready
      port: 8000
    initialDelaySeconds: 10
    periodSeconds: 5

# 前端配置
frontend:
  replicaCount: 2
  image:
    repository: ghcr.io/example/saltshark/frontend
    tag: latest
    pullPolicy: IfNotPresent
  
  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 512Mi
  
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70

# PostgreSQL 配置
postgresql:
  enabled: true
  auth:
    username: saltshark
    password: "changeme"  # 生产环境使用 Secret
    database: saltshark
  primary:
    persistence:
      enabled: true
      size: 20Gi
      storageClass: local-path
    resources:
      requests:
        cpu: 1000m
        memory: 2Gi
      limits:
        cpu: 4000m
        memory: 4Gi

# Redis 配置
redis:
  enabled: true
  auth:
    enabled: false
  master:
    persistence:
      enabled: true
      size: 5Gi
    resources:
      requests:
        cpu: 200m
        memory: 256Mi
      limits:
        cpu: 1000m
        memory: 512Mi

# OpenFGA 配置
openfga:
  enabled: true
  replicaCount: 2
  image:
    repository: openfga/openfga
    tag: latest
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 1Gi

# Celery Worker 配置
celeryWorker:
  replicaCount: 3
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi

# Celery Beat 配置
celeryBeat:
  replicaCount: 1
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 256Mi

# Ingress 配置
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: saltshark.example.com
      paths:
        - path: /api
          pathType: Prefix
          backend:
            service:
              name: saltshark-backend
              port: 8000
        - path: /
          pathType: Prefix
          backend:
            service:
              name: saltshark-frontend
              port: 3000
  tls:
    - secretName: saltshark-tls
      hosts:
        - saltshark.example.com
```

### 11.3 Deployment 模板示例

**backend-deployment.yaml**:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "saltshark.fullname" . }}-backend
  labels:
    {{- include "saltshark.labels" . | nindent 4 }}
    app.kubernetes.io/component: backend
spec:
  replicas: {{ .Values.backend.replicaCount }}
  selector:
    matchLabels:
      {{- include "saltshark.selectorLabels" . | nindent 6 }}
      app.kubernetes.io/component: backend
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        checksum/secret: {{ include (print $.Template.BasePath "/secret.yaml") . | sha256sum }}
      labels:
        {{- include "saltshark.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: backend
    spec:
      {{- with .Values.global.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      containers:
      - name: backend
        image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
        imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        env:
          {{- toYaml .Values.backend.env | nindent 10 }}
        livenessProbe:
          {{- toYaml .Values.backend.livenessProbe | nindent 10 }}
        readinessProbe:
          {{- toYaml .Values.backend.readinessProbe | nindent 10 }}
        resources:
          {{- toYaml .Values.backend.resources | nindent 10 }}
      restartPolicy: Always
```

### 11.4 滚动更新策略

**更新配置**:

```yaml
# backend-deployment.yaml (添加到 spec)
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1          # 最多额外创建 1 个 Pod
    maxUnavailable: 0    # 更新期间保持服务可用
```

**更新命令**:

```bash
# 更新后端
helm upgrade saltshark ./helm/saltshark \
  --set backend.image.tag=v1.2.0 \
  --namespace saltshark \
  --wait

# 回滚
helm rollback saltshark --namespace saltshark
```

---

## 12. 监控与运维

### 12.1 Prometheus 监控

#### 12.1.1 Metrics 暴露

**后端 Metrics** (`app/routers/metrics.py`):

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import APIRouter, Response

router = APIRouter()

# 定义指标
http_requests_total = Counter(
    "saltshark_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "saltshark_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

salt_api_requests_total = Counter(
    "saltshark_salt_api_requests_total",
    "Total Salt API requests",
    ["function", "status"]
)

salt_api_request_duration_seconds = Histogram(
    "saltshark_salt_api_request_duration_seconds",
    "Salt API request duration in seconds",
    ["function"]
)

minions_total = Gauge(
    "saltshark_minions_total",
    "Total number of minions",
    ["status"]
)

jobs_total = Counter(
    "saltshark_jobs_total",
    "Total number of jobs",
    ["status"]
)

@router.get("/metrics")
async def metrics():
    """暴露 Prometheus Metrics"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

**中间件集成**:

```python
from starlette.middleware.base import BaseHTTPMiddleware
import time

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # 记录指标
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response

# 添加到 FastAPI 应用
app.add_middleware(PrometheusMiddleware)
```

#### 12.1.2 ServiceMonitor 配置

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: saltshark-backend
  namespace: saltshark
  labels:
    app: saltshark
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: saltshark
      app.kubernetes.io/component: backend
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
    scrapeTimeout: 10s
```

### 12.2 Grafana Dashboard

#### 12.2.1 Dashboard JSON 配置

**主要面板**:

1. **系统概览**
   - QPS (Query Per Second)
   - 平均响应时间
   - 错误率
   - Minion 在线数量

2. **Salt API 监控**
   - Salt API 请求数
   - Salt API 响应时间分布
   - Salt API 错误率

3. **任务监控**
   - 任务创建速率
   - 任务成功/失败比例
   - 任务执行时间分布

4. **资源使用**
   - CPU 使用率
   - 内存使用率
   - 磁盘 I/O
   - 网络流量

**PromQL 查询示例**:

```promql
# QPS
rate(saltshark_http_requests_total[5m])

# 平均响应时间
rate(saltshark_http_request_duration_seconds_sum[5m]) 
  / 
rate(saltshark_http_request_duration_seconds_count[5m])

# 错误率
sum(rate(saltshark_http_requests_total{status=~"5.."}[5m])) 
  / 
sum(rate(saltshark_http_requests_total[5m]))

# Minion 在线数
saltshark_minions_total{status="online"}

# P95 响应时间
histogram_quantile(0.95, 
  rate(saltshark_http_request_duration_seconds_bucket[5m])
)
```

### 12.3 日志聚合

#### 12.3.1 结构化日志

**Python 日志配置** (`app/core/logging.py`):

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON 格式日志"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # 添加额外字段
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        # 添加异常信息
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ]
)

# 应用 JSON Formatter
for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

#### 12.3.2 Loki 集成

**Promtail 配置**:

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_name]
        action: keep
        regex: saltshark
      - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_component]
        target_label: component
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
    pipeline_stages:
      - json:
          expressions:
            timestamp: timestamp
            level: level
            message: message
            user_id: user_id
      - labels:
          level:
          user_id:
```

### 12.4 告警规则

#### 12.4.1 PrometheusRule 配置

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: saltshark-alerts
  namespace: saltshark
spec:
  groups:
  - name: saltshark
    interval: 30s
    rules:
    # 高错误率告警
    - alert: HighErrorRate
      expr: |
        sum(rate(saltshark_http_requests_total{status=~"5.."}[5m])) 
          / 
        sum(rate(saltshark_http_requests_total[5m])) > 0.05
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "SaltShark 错误率过高"
        description: "过去 5 分钟错误率超过 5%: {{ $value | humanizePercentage }}"
    
    # 响应时间过长告警
    - alert: HighLatency
      expr: |
        histogram_quantile(0.95, 
          rate(saltshark_http_request_duration_seconds_bucket[5m])
        ) > 2
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "SaltShark 响应时间过长"
        description: "P95 响应时间超过 2 秒: {{ $value }}s"
    
    # Salt API 不可用告警
    - alert: SaltAPIDown
      expr: |
        up{job="salt-api"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Salt API 不可用"
        description: "Salt API 已宕机超过 1 分钟"
    
    # 数据库连接池耗尽告警
    - alert: DatabaseConnectionPoolExhausted
      expr: |
        saltshark_database_connections_in_use 
          / 
        saltshark_database_connections_max > 0.9
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "数据库连接池即将耗尽"
        description: "连接池使用率超过 90%: {{ $value | humanizePercentage }}"
    
    # Pod 重启频繁告警
    - alert: PodRestartingFrequently
      expr: |
        rate(kube_pod_container_status_restarts_total{namespace="saltshark"}[1h]) > 0.1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Pod 重启过于频繁"
        description: "{{ $labels.pod }} 在过去 1 小时内重启超过 6 次"
```

#### 12.4.2 AlertManager 配置

```yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  routes:
  - match:
      severity: critical
    receiver: 'critical'
  - match:
      severity: warning
    receiver: 'warning'

receivers:
- name: 'default'
  webhook_configs:
  - url: 'http://alertmanager-webhook:8080/webhook'

- name: 'critical'
  webhook_configs:
  - url: 'http://alertmanager-webhook:8080/webhook/critical'
  # 可添加其他通知渠道
  # email_configs:
  # - to: 'ops@example.com'
  # slack_configs:
  # - channel: '#alerts'

- name: 'warning'
  webhook_configs:
  - url: 'http://alertmanager-webhook:8080/webhook/warning'
```

### 12.5 健康检查

**健康检查端点** (`app/routers/health.py`):

```python
from fastapi import APIRouter, status
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str
    dependencies: dict[str, str]

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """基础健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "dependencies": {}
    }

@router.get("/health/ready")
async def readiness_check():
    """就绪检查（检查所有依赖）"""
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "salt_api": await check_salt_api(),
        "openfga": await check_openfga(),
    }
    
    all_healthy = all(checks.values())
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks
    }, 200 if all_healthy else 503

async def check_database() -> bool:
    """检查数据库连接"""
    try:
        await db.execute_query("SELECT 1")
        return True
    except Exception:
        return False

async def check_redis() -> bool:
    """检查 Redis 连接"""
    try:
        await redis_client.ping()
        return True
    except Exception:
        return False

async def check_salt_api() -> bool:
    """检查 Salt API 连接"""
    try:
        await salt_client.login()
        return True
    except Exception:
        return False

async def check_openfga() -> bool:
    """检查 OpenFGA 连接"""
    try:
        await permission_service.check_health()
        return True
    except Exception:
        return False
```

---

## 13. 总结

本技术实现方案涵盖了 SaltShark 项目的完整技术架构，从后端到前端，从开发到部署，从监控到运维。主要亮点包括：

### 技术选型优势
- **现代化技术栈**: Python 3.11+, Next.js 16, TypeScript
- **高性能**: FasterApp (FastAPI), TortoiseORM 异步架构
- **可扩展性**: Kubernetes + HPA 自动扩缩容
- **安全可靠**: OpenFGA 细粒度权限, Keycloak SSO

### 架构设计原则
- **关注点分离**: 前后端分离，微服务化
- **零信任安全**: 所有请求验证权限，审计日志完整
- **高可用**: 多副本部署，自动故障转移
- **可观测性**: 完整的监控、日志、告警体系

### 开发体验
- **TDD 驱动**: 测试先行，80%+ 覆盖率
- **类型安全**: Python Type Hints + TypeScript
- **开发环境**: Docker Compose 一键启动
- **CI/CD**: 自动化测试、构建、部署

### 运维友好
- **容器化部署**: Docker + Kubernetes
- **GitOps**: Helm Chart + ArgoCD
- **监控告警**: Prometheus + Grafana + AlertManager
- **日志聚合**: Loki + Promtail 结构化日志

本方案为 SaltShark 项目提供了坚实的技术基础，确保系统的高性能、高可用、高安全性，同时保持良好的开发体验和运维效率。

---

## 14. 性能优化

### 14.1 后端性能优化

#### 14.1.1 数据库查询优化

**索引策略**:

```python
# TortoiseORM 索引定义
class Minion(Model):
    class Meta:
        indexes = [
            ("minion_id",),                    # 主键查询
            ("status", "last_seen"),           # 状态过滤 + 排序
            ("created_at",),                   # 时间范围查询
            Index(fields=["tags"], name="idx_tags"),  # GIN 索引（JSON）
        ]

class Job(Model):
    class Meta:
        indexes = [
            ("jid",),                          # 主键查询
            ("created_by", "created_at"),      # 用户任务列表
            ("status", "created_at"),          # 状态过滤 + 排序
            ("target",),                       # 目标查询
        ]
```

**查询优化示例**:

```python
# ❌ N+1 查询问题
async def get_jobs_with_users_bad():
    jobs = await Job.all()
    for job in jobs:
        user = await get_user_info(job.created_by)  # N 次查询
        job.user_name = user.display_name
    return jobs

# ✅ 批量查询优化
async def get_jobs_with_users_good():
    jobs = await Job.all()
    user_ids = [job.created_by for job in jobs]
    users = await user_info_service.get_users_batch(user_ids)  # 1 次批量查询
    
    for job in jobs:
        user = users.get(job.created_by)
        job.user_name = user.display_name if user else "未知用户"
    return jobs
```

**分页优化（游标分页）**:

```python
from typing import Optional

async def get_minions_cursor_pagination(
    cursor: Optional[str] = None,
    limit: int = 20
) -> dict:
    """游标分页，避免大偏移量性能问题"""
    query = Minion.all().order_by("-created_at")
    
    if cursor:
        # 解码游标获取上次查询的最后一条记录
        last_created_at = decode_cursor(cursor)
        query = query.filter(created_at__lt=last_created_at)
    
    minions = await query.limit(limit + 1)
    
    has_next = len(minions) > limit
    if has_next:
        minions = minions[:limit]
    
    next_cursor = None
    if has_next and minions:
        next_cursor = encode_cursor(minions[-1].created_at)
    
    return {
        "items": minions,
        "next_cursor": next_cursor,
        "has_next": has_next
    }
```

#### 14.1.2 缓存策略

**多级缓存架构**:

```python
from functools import wraps
import hashlib

class CacheService:
    """多级缓存服务"""
    
    def __init__(self, redis_client, local_cache_size=1000):
        self.redis = redis_client
        self.local_cache = LRUCache(maxsize=local_cache_size)
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存（L1 本地 -> L2 Redis）"""
        # L1: 本地缓存
        value = self.local_cache.get(key)
        if value is not None:
            return value
        
        # L2: Redis 缓存
        value = await self.redis.get(key)
        if value:
            # 回填本地缓存
            self.local_cache.set(key, value)
            return value
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 300
    ):
        """设置缓存（同时更新 L1 和 L2）"""
        self.local_cache.set(key, value)
        await self.redis.setex(key, ttl, value)
    
    async def delete(self, key: str):
        """删除缓存"""
        self.local_cache.delete(key)
        await self.redis.delete(key)

# 装饰器封装
def cache_result(ttl: int = 300, key_prefix: str = ""):
    """缓存函数结果"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存 Key
            cache_key = f"{key_prefix}:{func.__name__}:{_generate_cache_key(args, kwargs)}"
            
            # 尝试从缓存获取
            cached = await cache_service.get(cache_key)
            if cached:
                return cached
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 写入缓存
            await cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# 使用示例
@cache_result(ttl=300, key_prefix="minion")
async def get_minion_detail(minion_id: str) -> Minion:
    return await Minion.get(minion_id=minion_id)
```

#### 14.1.3 异步任务优化

**Celery 任务配置**:

```python
# celeryconfig.py
from kombu import Queue, Exchange

# Broker 配置
broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/1"

# 性能优化
task_acks_late = True              # 任务确认后置，防止任务丢失
worker_prefetch_multiplier = 4     # 预取任务数
task_compression = "gzip"          # 任务压缩
result_compression = "gzip"        # 结果压缩
task_time_limit = 300              # 硬超时 5 分钟
task_soft_time_limit = 270         # 软超时 4.5 分钟

# 队列优先级
task_queues = (
    Queue("high_priority", Exchange("high_priority"), routing_key="high"),
    Queue("normal", Exchange("normal"), routing_key="normal"),
    Queue("low_priority", Exchange("low_priority"), routing_key="low"),
)

# 任务路由
task_routes = {
    "app.tasks.minion.refresh_minion": {"queue": "high_priority"},
    "app.tasks.minion.sync_all_minions": {"queue": "low_priority"},
    "app.tasks.job.cleanup_old_jobs": {"queue": "low_priority"},
}
```

**任务批处理**:

```python
@celery_app.task
async def batch_refresh_minions(minion_ids: List[str]):
    """批量刷新 Minion（减少任务开销）"""
    # 分批处理，每批 50 个
    batch_size = 50
    for i in range(0, len(minion_ids), batch_size):
        batch = minion_ids[i:i + batch_size]
        
        # 并发执行
        tasks = [refresh_single_minion(mid) for mid in batch]
        await asyncio.gather(*tasks, return_exceptions=True)
```

### 14.2 前端性能优化

#### 14.2.1 代码分割和懒加载

```typescript
// app/layout.tsx
import dynamic from "next/dynamic";

// 动态导入大组件
const HeavyComponent = dynamic(
  () => import("@/components/HeavyComponent"),
  {
    loading: () => <Spinner />,
    ssr: false,  // 禁用服务端渲染
  }
);

// 路由级别代码分割（Next.js 16 自动支持）
// app/minions/[id]/page.tsx 会自动分割为独立的 chunk
```

#### 14.2.2 数据预取和缓存

```typescript
// React Query 配置
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30000,              // 30 秒内数据视为新鲜
      cacheTime: 300000,             // 缓存保留 5 分钟
      refetchOnWindowFocus: false,   // 窗口聚焦不自动刷新
      retry: 2,                      // 失败重试 2 次
    },
  },
});

// 预取数据
export function useMinionListWithPrefetch() {
  const queryClient = useQueryClient();
  
  const { data } = useQuery({
    queryKey: ["minions"],
    queryFn: fetchMinions,
    onSuccess: (data) => {
      // 预取每个 Minion 的详情页
      data.items.forEach((minion) => {
        queryClient.prefetchQuery({
          queryKey: ["minion", minion.minion_id],
          queryFn: () => fetchMinionDetail(minion.minion_id),
        });
      });
    },
  });
  
  return data;
}
```

#### 14.2.3 虚拟滚动

```typescript
// 使用 @tanstack/react-virtual 处理大列表
import { useVirtualizer } from "@tanstack/react-virtual";
import { useRef } from "react";

export function VirtualMinionList({ minions }: { minions: Minion[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: minions.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 80,  // 每行高度
    overscan: 5,             // 预渲染 5 行
  });
  
  return (
    <div ref={parentRef} style={{ height: "600px", overflow: "auto" }}>
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          position: "relative",
        }}
      >
        {virtualizer.getVirtualItems().map((virtualRow) => {
          const minion = minions[virtualRow.index];
          return (
            <div
              key={virtualRow.key}
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "100%",
                height: `${virtualRow.size}px`,
                transform: `translateY(${virtualRow.start}px)`,
              }}
            >
              <MinionCard minion={minion} />
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

### 14.3 Salt API 性能优化

#### 14.3.1 连接池管理

```python
import httpx
from asyncio import Semaphore

class SaltAPIConnectionPool:
    """Salt API 连接池"""
    
    def __init__(
        self,
        api_url: str,
        username: str,
        password: str,
        max_connections: int = 50,
        max_keepalive_connections: int = 20
    ):
        self.api_url = api_url
        self.username = username
        self.password = password
        
        # 创建连接池
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=60.0
        )
        
        self.client = httpx.AsyncClient(
            base_url=api_url,
            limits=limits,
            timeout=30.0,
            http2=True  # 启用 HTTP/2
        )
        
        # 并发控制
        self.semaphore = Semaphore(max_connections)
        
        # Token 管理
        self.token: Optional[str] = None
        self.token_lock = asyncio.Lock()
    
    async def execute_with_concurrency_limit(
        self,
        target: str,
        function: str,
        **kwargs
    ):
        """带并发控制的命令执行"""
        async with self.semaphore:
            return await self._execute_command(target, function, **kwargs)
```

#### 14.3.2 批量操作优化

```python
async def batch_get_minion_grains(
    minion_ids: List[str],
    batch_size: int = 100
) -> Dict[str, Dict]:
    """批量获取 Minion Grains（分批执行）"""
    results = {}
    
    # 分批执行，避免单次请求过大
    for i in range(0, len(minion_ids), batch_size):
        batch = minion_ids[i:i + batch_size]
        
        # 使用 Salt 的 list target type
        result = await salt_client.execute_command(
            target=",".join(batch),
            function="grains.items",
            target_type="list"
        )
        
        results.update(result.get("return", [{}])[0])
    
    return results
```

### 14.4 性能监控指标

**关键性能指标 (KPI)**:

| 指标 | 目标值 | 说明 |
|------|--------|------|
| API 响应时间 (P95) | < 500ms | 95% 的请求在 500ms 内响应 |
| API 响应时间 (P99) | < 1s | 99% 的请求在 1s 内响应 |
| 页面加载时间 (FCP) | < 1.5s | First Contentful Paint |
| 页面交互时间 (TTI) | < 3s | Time to Interactive |
| 数据库查询时间 | < 50ms | 单次查询平均时间 |
| Redis 查询时间 | < 5ms | 单次查询平均时间 |
| Salt API 调用时间 | < 2s | 单次调用平均时间 |
| Minion 列表加载 (1000台) | < 3s | 包含渲染时间 |
| Job 执行响应 | < 200ms | 提交任务的响应时间 |

---

## 15. 安全加固

### 15.1 API 安全

#### 15.1.1 请求限流

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# 创建限流器
limiter = Limiter(key_func=get_remote_address)

# FastAPI 集成
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 应用到路由
@router.post("/jobs/execute")
@limiter.limit("10/minute")  # 每分钟最多 10 次
async def execute_job(request: Request, ...):
    """执行任务（限流保护）"""
    pass

# 基于用户的限流
@router.get("/minions")
@limiter.limit("100/minute", key_func=lambda request: request.state.user_id)
async def get_minions(request: Request, ...):
    """获取 Minion 列表（按用户限流）"""
    pass
```

#### 15.1.2 输入验证

```python
from pydantic import BaseModel, validator, constr, conint
import re

class JobExecuteRequest(BaseModel):
    """任务执行请求（严格验证）"""
    
    target: constr(min_length=1, max_length=500)
    target_type: str
    function: constr(min_length=1, max_length=100)
    args: List[str] = []
    kwargs: Dict[str, Any] = {}
    
    @validator("target_type")
    def validate_target_type(cls, v):
        """验证目标类型"""
        allowed = ["glob", "list", "grain", "compound"]
        if v not in allowed:
            raise ValueError(f"target_type 必须是 {allowed} 之一")
        return v
    
    @validator("function")
    def validate_function(cls, v):
        """验证函数名（防止命令注入）"""
        # 只允许字母、数字、下划线、点号
        if not re.match(r"^[a-zA-Z0-9_.]+$", v):
            raise ValueError("function 包含非法字符")
        
        # 黑名单检查
        blacklist = ["cmd.run", "cmd.shell"]  # 根据实际情况配置
        if v in blacklist:
            raise ValueError(f"禁止使用函数: {v}")
        
        return v
    
    @validator("args")
    def validate_args(cls, v):
        """验证参数（防止注入）"""
        for arg in v:
            # 检查危险字符
            if any(char in arg for char in [";", "|", "&", "$", "`"]):
                raise ValueError("参数包含危险字符")
        return v
```

#### 15.1.3 SQL 注入防护

```python
# ✅ 使用 ORM 参数化查询
async def search_minions_safe(keyword: str):
    """安全的搜索（使用 ORM）"""
    return await Minion.filter(
        Q(minion_id__icontains=keyword) |
        Q(grains__hostname__icontains=keyword)
    )

# ❌ 避免字符串拼接（SQL 注入风险）
async def search_minions_unsafe(keyword: str):
    """不安全的搜索（SQL 注入风险）"""
    query = f"SELECT * FROM minions WHERE minion_id LIKE '%{keyword}%'"
    return await db.execute_query(query)
```

### 15.2 认证和授权加固

#### 15.2.1 Token 刷新策略

```python
from datetime import datetime, timedelta
import jwt

async def refresh_access_token(refresh_token: str) -> dict:
    """刷新访问令牌"""
    try:
        # 验证 Refresh Token
        payload = jwt.decode(
            refresh_token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        
        user_id = payload.get("sub")
        
        # 检查 Token 是否被撤销
        is_revoked = await redis_client.get(f"revoked_token:{refresh_token}")
        if is_revoked:
            raise HTTPException(401, "Token 已被撤销")
        
        # 生成新的 Access Token
        access_token = generate_access_token(
            user_id=user_id,
            expires_delta=timedelta(minutes=15)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 900
        }
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Refresh Token 已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "无效的 Refresh Token")

async def revoke_token(token: str):
    """撤销 Token（登出）"""
    # 将 Token 加入黑名单，设置过期时间
    await redis_client.setex(
        f"revoked_token:{token}",
        3600 * 24,  # 24 小时
        "1"
    )
```

#### 15.2.2 CSRF 防护

```python
from fastapi import Request, HTTPException
import secrets

async def generate_csrf_token(user_id: str) -> str:
    """生成 CSRF Token"""
    token = secrets.token_urlsafe(32)
    await redis_client.setex(
        f"csrf_token:{user_id}:{token}",
        3600,  # 1 小时
        "1"
    )
    return token

async def verify_csrf_token(
    request: Request,
    user_id: str,
    token: str
):
    """验证 CSRF Token"""
    # 检查 Token 是否存在
    exists = await redis_client.get(f"csrf_token:{user_id}:{token}")
    if not exists:
        raise HTTPException(403, "CSRF Token 无效或已过期")
    
    # 删除 Token（一次性使用）
    await redis_client.delete(f"csrf_token:{user_id}:{token}")

# 中间件
class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 只检查修改类请求
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            token = request.headers.get("X-CSRF-Token")
            if not token:
                return JSONResponse(
                    {"detail": "缺少 CSRF Token"},
                    status_code=403
                )
            
            user_id = request.state.user_id
            await verify_csrf_token(request, user_id, token)
        
        return await call_next(request)
```

### 15.3 数据加密

#### 15.3.1 敏感数据加密

```python
from cryptography.fernet import Fernet
import base64

class EncryptionService:
    """数据加密服务"""
    
    def __init__(self, key: str):
        self.fernet = Fernet(key.encode())
    
    def encrypt(self, data: str) -> str:
        """加密数据"""
        encrypted = self.fernet.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """解密数据"""
        encrypted = base64.b64decode(encrypted_data.encode())
        decrypted = self.fernet.decrypt(encrypted)
        return decrypted.decode()

# 使用示例：加密 Salt API 密码
class SaltAPICredential(Model):
    username = fields.CharField(max_length=100)
    password_encrypted = fields.TextField()
    
    @property
    def password(self) -> str:
        """获取解密后的密码"""
        return encryption_service.decrypt(self.password_encrypted)
    
    @password.setter
    def password(self, value: str):
        """设置加密的密码"""
        self.password_encrypted = encryption_service.encrypt(value)
```

### 15.4 安全审计

#### 15.4.1 审计日志中间件

```python
class AuditLogMiddleware(BaseHTTPMiddleware):
    """审计日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 记录请求信息
        request_data = {
            "user_id": getattr(request.state, "user_id", None),
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent"),
        }
        
        # 敏感数据脱敏
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                request_data["body"] = self._mask_sensitive_data(
                    json.loads(body)
                )
            except:
                pass
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # 记录审计日志
        await AuditLog.create(
            user_id=request_data["user_id"],
            action=f"{request.method} {request.url.path}",
            resource_type=self._extract_resource_type(request.url.path),
            resource_id=self._extract_resource_id(request.url.path),
            details=request_data,
            ip_address=request_data["ip_address"],
            user_agent=request_data["user_agent"],
            status_code=response.status_code,
            duration=duration
        )
        
        return response
    
    def _mask_sensitive_data(self, data: dict) -> dict:
        """脱敏敏感数据"""
        sensitive_keys = ["password", "token", "secret", "api_key"]
        
        masked = data.copy()
        for key in masked:
            if any(s in key.lower() for s in sensitive_keys):
                masked[key] = "***MASKED***"
        
        return masked
```

---

## 16. 容灾和备份

### 16.1 数据库备份策略

#### 16.1.1 自动备份脚本

```bash
#!/bin/bash
# backup-postgres.sh - PostgreSQL 备份脚本

set -e

# 配置
BACKUP_DIR="/backup/postgres"
RETENTION_DAYS=30
POSTGRES_HOST="postgres"
POSTGRES_DB="saltshark"
POSTGRES_USER="saltshark"
S3_BUCKET="s3://backup-bucket/saltshark/postgres"

# 生成备份文件名
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="saltshark_${TIMESTAMP}.sql.gz"

# 执行备份
echo "开始备份数据库: ${POSTGRES_DB}"
pg_dump -h ${POSTGRES_HOST} -U ${POSTGRES_USER} ${POSTGRES_DB} | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# 上传到 S3
echo "上传备份到 S3"
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" "${S3_BUCKET}/${BACKUP_FILE}"

# 清理本地旧备份
echo "清理 ${RETENTION_DAYS} 天前的备份"
find ${BACKUP_DIR} -name "saltshark_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

# 清理 S3 旧备份
aws s3 ls ${S3_BUCKET}/ | while read -r line; do
    createDate=$(echo $line | awk {'print $1" "$2'})
    createDate=$(date -d "$createDate" +%s)
    olderThan=$(date -d "${RETENTION_DAYS} days ago" +%s)
    if [[ $createDate -lt $olderThan ]]; then
        fileName=$(echo $line | awk {'print $4'})
        if [[ $fileName != "" ]]; then
            aws s3 rm ${S3_BUCKET}/${fileName}
        fi
    fi
done

echo "备份完成: ${BACKUP_FILE}"
```

#### 16.1.2 Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: saltshark
spec:
  schedule: "0 2 * * *"  # 每天凌晨 2 点
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: access-key-id
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: aws-credentials
                  key: secret-access-key
            volumeMounts:
            - name: backup-script
              mountPath: /scripts
            - name: backup-storage
              mountPath: /backup
            command:
            - /bin/bash
            - /scripts/backup-postgres.sh
          restartPolicy: OnFailure
          volumes:
          - name: backup-script
            configMap:
              name: backup-scripts
              defaultMode: 0755
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
```

### 16.2 灾难恢复

#### 16.2.1 数据恢复流程

```bash
#!/bin/bash
# restore-postgres.sh - PostgreSQL 恢复脚本

set -e

BACKUP_FILE=$1
POSTGRES_HOST="postgres"
POSTGRES_DB="saltshark"
POSTGRES_USER="saltshark"

if [ -z "$BACKUP_FILE" ]; then
    echo "用法: $0 <backup_file>"
    exit 1
fi

# 下载备份文件（如果是 S3 路径）
if [[ $BACKUP_FILE == s3://* ]]; then
    LOCAL_FILE="/tmp/$(basename $BACKUP_FILE)"
    echo "从 S3 下载备份文件"
    aws s3 cp $BACKUP_FILE $LOCAL_FILE
    BACKUP_FILE=$LOCAL_FILE
fi

# 停止应用（可选，确保数据一致性）
echo "停止应用服务"
kubectl scale deployment saltshark-backend --replicas=0 -n saltshark

# 删除现有数据库
echo "删除现有数据库"
psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -c "DROP DATABASE IF EXISTS ${POSTGRES_DB};"

# 创建新数据库
echo "创建新数据库"
psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} -c "CREATE DATABASE ${POSTGRES_DB};"

# 恢复数据
echo "恢复数据"
gunzip -c ${BACKUP_FILE} | psql -h ${POSTGRES_HOST} -U ${POSTGRES_USER} ${POSTGRES_DB}

# 重启应用
echo "重启应用服务"
kubectl scale deployment saltshark-backend --replicas=3 -n saltshark

echo "恢复完成"
```

#### 16.2.2 RTO/RPO 目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| RPO (Recovery Point Objective) | 24 小时 | 最多丢失 24 小时数据 |
| RTO (Recovery Time Objective) | 4 小时 | 4 小时内恢复服务 |
| 备份频率 | 每天 1 次 | 每日凌晨自动备份 |
| 备份保留期 | 30 天 | 保留最近 30 天备份 |
| 备份存储 | S3 + 本地 | 双重保障 |

### 16.3 高可用配置

#### 16.3.1 PostgreSQL 主从复制

```yaml
# PostgreSQL Streaming Replication
# values-ha.yaml (Helm Chart)

postgresql:
  architecture: replication
  replication:
    enabled: true
    numSynchronousReplicas: 1
    synchronousCommit: "on"
  
  primary:
    persistence:
      enabled: true
      size: 50Gi
    resources:
      requests:
        cpu: 2000m
        memory: 4Gi
      limits:
        cpu: 4000m
        memory: 8Gi
  
  readReplicas:
    replicaCount: 2
    persistence:
      enabled: true
      size: 50Gi
    resources:
      requests:
        cpu: 1000m
        memory: 2Gi
      limits:
        cpu: 2000m
        memory: 4Gi
```

#### 16.3.2 Redis 哨兵模式

```yaml
# Redis Sentinel 配置
redis:
  architecture: replication
  sentinel:
    enabled: true
    quorum: 2
    downAfterMilliseconds: 5000
    failoverTimeout: 10000
  
  master:
    persistence:
      enabled: true
      size: 10Gi
  
  replica:
    replicaCount: 2
    persistence:
      enabled: true
      size: 10Gi
```

---

## 17. 文档和培训

### 17.1 技术文档结构

```
docs/
├── README.md                          # 项目概述
├── getting-started/                   # 快速开始
│   ├── installation.md               # 安装指南
│   ├── configuration.md              # 配置说明
│   └── first-deployment.md           # 首次部署
├── architecture/                      # 架构文档
│   ├── overview.md                   # 架构概览
│   ├── backend.md                    # 后端架构
│   ├── frontend.md                   # 前端架构
│   └── security.md                   # 安全架构
├── api/                              # API 文档
│   ├── authentication.md             # 认证说明
│   ├── minions.md                    # Minion API
│   ├── jobs.md                       # Job API
│   └── permissions.md                # 权限 API
├── development/                       # 开发文档
│   ├── setup.md                      # 开发环境设置
│   ├── coding-standards.md           # 编码规范
│   ├── testing.md                    # 测试指南
│   └── contributing.md               # 贡献指南
├── deployment/                        # 部署文档
│   ├── kubernetes.md                 # K8s 部署
│   ├── helm-values.md                # Helm 配置
│   └── troubleshooting.md            # 故障排查
└── operations/                        # 运维文档
    ├── monitoring.md                 # 监控配置
    ├── backup-restore.md             # 备份恢复
    ├── disaster-recovery.md          # 灾难恢复
    └── performance-tuning.md         # 性能调优
```

### 17.2 用户手册

**用户手册目录** (`docs/user-guide/`):

1. **入门指南**
   - 登录系统
   - 界面导航
   - 基本概念

2. **Minion 管理**
   - 查看 Minion 列表
   - 接受新 Minion
   - 刷新 Minion 数据
   - 标签管理

3. **远程执行**
   - 执行命令
   - 查看执行结果
   - 任务历史

4. **权限管理**
   - 权限模型说明
   - 分配权限
   - 权限审查

5. **审计日志**
   - 查看操作日志
   - 日志过滤
   - 导出日志

### 17.3 API 文档生成

**Swagger/OpenAPI 配置**:

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="SaltShark API",
    description="SaltShark 管理平台 RESTful API",
    version="1.0.0",
    contact={
        "name": "SaltShark Team",
        "email": "team@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # 添加安全方案
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 访问 API 文档:
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
# - OpenAPI JSON: http://localhost:8000/openapi.json
```

---

## 18. 项目交付清单

### 18.1 代码交付

- [ ] 后端代码（Python/FasterApp）
  - [ ] API 路由实现
  - [ ] 数据库模型
  - [ ] 权限中间件
  - [ ] 单元测试（覆盖率 ≥ 80%）
  - [ ] 集成测试

- [ ] 前端代码（Next.js/TypeScript）
  - [ ] 页面组件
  - [ ] API 客户端
  - [ ] 状态管理
  - [ ] 单元测试
  - [ ] E2E 测试

- [ ] 基础设施代码
  - [ ] Kubernetes 清单
  - [ ] Helm Charts
  - [ ] Terraform 脚本（可选）
  - [ ] CI/CD 流水线

### 18.2 配置文件

- [ ] 环境配置
  - [ ] 开发环境配置
  - [ ] 测试环境配置
  - [ ] 生产环境配置

- [ ] 依赖配置
  - [ ] requirements.txt (Python)
  - [ ] package.json (Node.js)
  - [ ] Dockerfile
  - [ ] docker-compose.yml

- [ ] 服务配置
  - [ ] PostgreSQL 配置
  - [ ] Redis 配置
  - [ ] OpenFGA 配置
  - [ ] Keycloak 配置

### 18.3 文档交付

- [ ] 技术文档
  - [ ] 架构设计文档
  - [ ] API 文档
  - [ ] 数据库 ER 图
  - [ ] 部署文档

- [ ] 用户文档
  - [ ] 用户手册
  - [ ] 快速开始指南
  - [ ] 常见问题 FAQ

- [ ] 运维文档
  - [ ] 监控配置文档
  - [ ] 备份恢复流程
  - [ ] 故障排查手册
  - [ ] 性能调优指南

### 18.4 质量保证

- [ ] 代码质量
  - [ ] 代码审查完成
  - [ ] 静态代码分析通过
  - [ ] 测试覆盖率达标

- [ ] 性能测试
  - [ ] 压力测试报告
  - [ ] 性能基准测试
  - [ ] 性能优化建议

- [ ] 安全审计
  - [ ] 安全扫描报告
  - [ ] 漏洞修复记录
  - [ ] 安全最佳实践检查

### 18.5 培训材料

- [ ] 开发者培训
  - [ ] 代码结构讲解
  - [ ] 开发环境搭建
  - [ ] 编码规范培训

- [ ] 运维培训
  - [ ] 部署流程培训
  - [ ] 监控配置培训
  - [ ] 故障处理培训

- [ ] 用户培训
  - [ ] 功能演示视频
  - [ ] 操作手册
  - [ ] 在线培训课程

---

## 19. 总结

本技术实现方案为 SaltShark 项目提供了全面的技术指导，涵盖了从架构设计到实施部署的各个方面。

### 19.1 技术亮点

1. **现代化技术栈**
   - Python 3.11+ 异步架构，高性能处理
   - Next.js 16 服务端渲染，优秀的用户体验
   - OpenFGA 细粒度权限，灵活的访问控制

2. **可靠的架构设计**
   - 前后端分离，职责清晰
   - 微服务化设计，易于扩展
   - 多级缓存策略，性能优化

3. **完善的安全机制**
   - 零信任架构，层层防护
   - 完整的审计日志，合规要求
   - 数据加密传输和存储

4. **优秀的运维能力**
   - Kubernetes 容器化部署
   - GitOps 自动化流程
   - 完整的监控告警体系

### 19.2 实施路线图

**Phase 1: MVP (2-3 个月)**
- ✅ 基础架构搭建
- ✅ 用户认证集成
- ✅ Minion 管理功能
- ✅ 基础权限控制
- ✅ 简单的任务执行

**Phase 2: 核心功能 (3-4 个月)**
- ✅ 完整的权限系统
- ✅ 审计日志
- ✅ 高级任务管理
- ✅ 监控告警
- ✅ 性能优化

**Phase 3: 增强功能 (2-3 个月)**
- ✅ 高可用部署
- ✅ 灾难恢复
- ✅ 高级分析
- ✅ 自动化运维

### 19.3 成功标准

- ✅ 支持 1,000-10,000 台 Minion
- ✅ API 响应时间 P95 < 500ms
- ✅ 系统可用性 99.9%
- ✅ 测试覆盖率 ≥ 80%
- ✅ 零安全漏洞
- ✅ 完整的文档和培训材料

本方案为 SaltShark 项目的成功实施奠定了坚实的技术基础，确保系统的高性能、高可用、高安全性，同时保持良好的开发体验和运维效率。
