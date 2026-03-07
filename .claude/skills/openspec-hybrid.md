# OpenSpec Hybrid Skill

## 目标
使用"对话驱动为主，命令驱动为辅"完成 OpenSpec 工作流。

## 默认行为
1. 对话中先澄清目标与约束
2. 先读 spec/index.md，再按需加载上下文
3. 在关键节点执行命令检查点：validate / compile / graph / loop

## 命令映射
- opsx:validate
- opsx:compile
- opsx:graph
- opsx:loop
