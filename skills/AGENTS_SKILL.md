---
name: knowhealth-agents
description: KnowHealth AI医患讨论室 — 4个AI Agent协同(协调员/翻译/总结/顾问)，跨境医疗第二意见平台
version: 1.1.0
category: healthcare
triggers:
  - 医患讨论
  - 第二意见
  - 跨境医疗
  - AI问诊
test_prompts:
  - "55岁肺腺癌EGFR突变患者寻求美国专家第二意见"
author: KnowHealth Team
---

# KnowHealth: AI Agent医患讨论室

## 四大Agent

### Agent-1: 协调员（小和）
引导讨论、分配任务、控制节奏。

### Agent-2: 翻译（小译）
中英文实时翻译，医学术语专业翻译。

### Agent-3: 总结（小结）
提取关键信息，生成结构化病历摘要。

### Agent-4: 顾问（小智）
基于循证医学提供建议，引用文献支持。

## 工作流程

### Step 1: 初始化讨论
⚠️ 确认检查点: 患者授权确认。

### Step 2: 信息收集
小和引导 → 小译翻译 → 小结记录

### Step 3: 医生评估
医生查看摘要 → 小智提供循证参考

### Step 4: 生成报告
中英双语报告 + 参考文献。

## 异常处理
| 场景 | 处理方式 |
|------|----------|
| 翻译超时 | 使用缓存翻译 |
| 医生离线 | AI顾问提供初步参考(标注"非诊断") |
| 敏感信息 | 自动脱敏 |
| 讨论中断 | 保存进度，断点续聊 |

## 安全合规
- 所有AI输出包含 `⚠️ AI辅助参考，非最终诊断`
- 数据AES-256加密
- 符合HIPAA/GDPR

## 参考文件
- iOS: `~/Desktop/KnowHealth-iOS/`
- 后端: `~/Desktop/KnowHealth/src/`
