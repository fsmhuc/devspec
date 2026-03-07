---
name: openspec-hybrid
description: OpenSpec 混合工作流技能 — 对话驱动为主，命令检查点为辅，驱动规格验证、编译、可视化与开发循环
---

# OpenSpec Hybrid Skill

## 目标
使用"对话驱动为主，命令驱动为辅"完成 OpenSpec 工作流。

## 默认行为
1. 对话中先澄清目标与约束
2. 先读 spec/index.md，再按需加载上下文
3. 在关键节点执行命令检查点：validate / compile / graph / loop

## 命令映射
- opsx:validate  -> python3 mcp/cli.py opsx:validate
- opsx:compile   -> python3 mcp/cli.py opsx:compile
- opsx:graph     -> python3 mcp/cli.py opsx:graph
- opsx:loop      -> python3 mcp/cli.py opsx:loop
- opsx:workflow  -> python3 mcp/cli.py workflow
