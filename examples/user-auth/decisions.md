# 功能决策 — 用户认证

> 记录用户认证功能的功能级别决策。架构级别决策见 `spec/decisions/`。

---

## 决策 1: 使用 bcrypt 哈希密码

**决策**: 使用 bcrypt（cost factor = 12）存储密码哈希

**原因**: bcrypt 专为密码设计，内置盐值，cost factor 可调

**备选方案**: 
- Argon2 — 更安全但生态支持不如 bcrypt 普及
- SHA256 + salt — 太快，不适合密码哈希

---

## 决策 2: Access Token + Refresh Token 双 Token 方案

**决策**: Access Token 短有效期（15min），Refresh Token 长有效期（7d）

**原因**: 平衡安全性和用户体验，Access Token 泄露影响有限

**备选方案**:
- 只用单 Token — 要么有效期太短（体验差）要么太长（不安全）
