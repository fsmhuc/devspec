---
name: devspec-hybrid
description: DevSpec 混合工作流技能 — 对话驱动为主，命令检查点为辅，驱动规格验证、编译、可视化与开发循环
---

# DevSpec Hybrid Skill

## 目标
使用"对话驱动为主，命令驱动为辅"完成 DevSpec 工作流。

## 默认行为
1. 对话中先澄清目标与约束
2. 先读 spec/index.md，再按需加载上下文
3. 在关键节点执行命令检查点：validate / compile / graph / loop

## 命令映射
- ds:validate  -> python3 mcp/cli.py ds:validate
- ds:compile   -> python3 mcp/cli.py ds:compile
- ds:graph     -> python3 mcp/cli.py ds:graph
- ds:loop      -> python3 mcp/cli.py ds:loop
- ds:workflow  -> python3 mcp/cli.py workflow
