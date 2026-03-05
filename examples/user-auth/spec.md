# 用户认证（User Auth）

> 状态: `in-progress`

---

## 目标

- 安全的用户登录/登出
- 密码重置流程
- 会话管理（基于 JWT）
- 支持多种认证方式扩展

---

## 非目标

- 不处理第三方 OAuth 登录（将来单独的功能）
- 不管理用户权限/角色（见未来的 RBAC 功能）

---

## 设计

### 概述

采用 JWT（RS256）无状态认证方案。用户通过用户名+密码登录，
服务端签发 JWT Token，客户端后续请求通过 Bearer Token 认证。

### 认证流程

```
客户端                    API                      数据库
  │                        │                        │
  │── POST /api/auth/login ──>│                        │
  │   {email, password}    │── 验证凭据 ──>            │
  │                        │<── 用户信息 ──             │
  │<── {token, expiresIn} ──│                        │
  │                        │                        │
  │── GET /api/xxx ────────>│                        │
  │   Authorization: Bearer │── 验证 JWT ──>           │
  │                        │<── 请求处理 ──             │
  │<── 响应数据 ──────────── │                        │
```

---

## 接口

### API 端点

| 方法 | 路径                       | 描述       | 请求体                | 响应                   |
| ---- | -------------------------- | ---------- | --------------------- | ---------------------- |
| POST | `/api/auth/login`          | 用户登录   | `{ email, password }` | `{ token, expiresIn }` |
| POST | `/api/auth/logout`         | 用户登出   | -                     | `{ success: true }`    |
| POST | `/api/auth/refresh`        | 刷新 Token | `{ refreshToken }`    | `{ token, expiresIn }` |
| POST | `/api/auth/reset-password` | 密码重置   | `{ email }`           | `{ message }`          |

### 数据模型

```json
{
  "id": "uuid",
  "email": "string",
  "passwordHash": "string (bcrypt)",
  "createdAt": "datetime",
  "lastLoginAt": "datetime"
}
```

---

## 验收标准

- [ ] 正确的用户名密码可以获得 JWT Token
- [ ] 错误的密码返回 401，不泄露用户是否存在
- [ ] Token 过期后返回 401
- [ ] 密码重置发送邮件链接
- [ ] 密码存储使用 bcrypt 哈希

---

## 约束条件

- 性能: 登录接口响应 < 500ms
- 安全: 密码最少 8 位，支持暴力破解防护（rate limiting）
- Token: Access Token 有效期 15 分钟，Refresh Token 7 天

---

## 依赖

| 依赖项   | 类型     | 状态   |
| -------- | -------- | ------ |
| 数据库   | 基础设施 | 可用   |
| 邮件服务 | 外部服务 | 待确认 |

---

## 风险

| 风险         | 可能性 | 影响 | 缓解方案                 |
| ------------ | ------ | ---- | ------------------------ |
| JWT 密钥泄露 | 低     | 高   | 密钥轮转机制 + 环境变量  |
| 暴力破解     | 中     | 中   | Rate limiting + 账户锁定 |

---

## 边界情况

- 当用户不存在时 → 返回通用错误，不暴露用户是否存在
- 当 Token 被篡改时 → RS256 签名验证失败，返回 401
- 当刷新 Token 过期时 → 用户需要重新登录
- 当邮件服务不可用时 → 密码重置返回友好错误，后台重试
