---
name: knowhealth-ai-agents
description: KnowHealth AI医患讨论室 — 4个AI Agent协同工作，协调员/翻译/总结/顾问，支持跨境医疗第二意见
version: 1.1.0
category: healthcare
triggers:
  - 医患讨论
  - 第二意见
  - 跨境医疗
  - AI问诊
  - 医疗咨询
author: KnowHealth Team
test_prompts:
  - "一位55岁男性，确诊肺腺癌EGFR突变，寻求第二意见"
  - "日本医生对治疗方案的建议需要翻译"
---

# KnowHealth: AI Agent医患讨论室

## 输入格式
```json
{
  "patient": {
    "age": 55,
    "gender": "male",
    "diagnosis": "肺腺癌 EGFR L858R突变",
    "stage": "IIIA",
    "prior_treatment": ["手术切除", "辅助化疗"]
  },
  "request_type": "second_opinion",
  "languages": ["zh", "en"],
  "preferred_doctor_region": "US"
}
```

## 四大Agent详细规格

### Agent-1: 协调员（小和）
**输入**: 患者信息 + 讨论目标
**输出**: 讨论议程 + 任务分配
```python
coordinator.process({
    "patient_info": {...},
    "discussion_goal": "second_opinion",
    "participants": ["patient", "doctor", "ai_advisor"]
})
# 输出:
{
    "agenda": ["信息收集", "医生评估", "AI参考", "总结报告"],
    "task_assignments": {
        "translator": "实时中英翻译",
        "summarizer": "记录关键信息",
        "advisor": "提供循证参考"
    }
}
```

### Agent-2: 翻译（小译）
**输入**: 原文 + 源语言 + 目标语言
**输出**: 翻译结果 + 医学术语对照
```python
translator.translate(
    text="The patient presents with EGFR L858R mutation...",
    source="en", target="zh",
    domain="oncology"
)
# 输出:
{
    "translation": "患者携带EGFR L858R突变...",
    "medical_terms": {"EGFR": "表皮生长因子受体", "L858R": "L858R突变"},
    "confidence": 0.98
}
```
⚠️ **确认检查点**: 翻译医学关键信息后，要求双方确认。

### Agent-3: 总结（小结）
**输入**: 讨论记录
**输出**: 结构化摘要
```python
summarizer.summarize(discussion_log)
# 输出:
{
    "chief_complaint": "...",
    "diagnosis": "...",
    "treatment_history": [...],
    "current_recommendation": "...",
    "uncertainties": ["...", "..."],
    "follow_up_needed": true
}
```
⚠️ **确认检查点**: 总结生成后需患者和医生确认。

### Agent-4: 顾问（小智）
**输入**: 患者信息 + 医生建议
**输出**: 循证参考 + 置信度
```python
advisor.provide_reference(
    condition="EGFR+ NSCLC IIIA",
    treatment="Osimertinib",
    recommendation_type="evidence_based"
)
# 输出:
{
    "references": [
        {"pmid": "34153108", "title": "FLAURA2 study...", "relevance": 0.95}
    ],
    "evidence_level": "HIGH",
    "confidence": 0.88,
    "disclaimer": "⚠️ AI辅助参考，非最终诊断。最终决策请遵医嘱。"
}
```

## 工作流程（完整示例）

### 场景: 肺癌患者寻求美国专家第二意见

**Phase 1: 初始化** (协调员主导)
1. 患者上传病历 → 系统解析 → 生成结构化摘要
2. 协调员创建讨论室，邀请医生
3. 分配翻译、总结、顾问Agent任务

**Phase 2: 信息补充** (翻译+总结协同)
1. 协调员引导患者补充关键信息
2. 翻译实时转换语言
3. 总结持续更新病历摘要
4. ⚠️ 关键信息确认检查点

**Phase 3: 医生评估** (顾问辅助)
1. 医生查看结构化摘要
2. 顾问提供相关文献和指南参考
3. 医生给出诊断和治疗建议
4. ⚠️ 诊断确认检查点

**Phase 4: 生成报告** (总结主导)
1. 总结生成中英双语报告
2. 包含: 诊断意见、治疗方案、参考文献、注意事项
3. ⚠️ 报告确认检查点
4. 输出PDF/可分享链接

## 异常处理

| 场景 | 处理方式 |
|------|----------|
| 翻译超时(>10s) | 使用缓存翻译，标注"待确认" |
| 医生离线 | AI顾问提供初步参考，大字标注"非诊断" |
| 敏感信息(身份证/电话) | 自动脱敏: `138****1234` |
| 讨论中断 | 保存进度，支持断点续聊 |
| 翻译置信度<0.8 | 标注"翻译不确定，请确认" |

## 安全合规
- 所有AI输出必须包含: `⚠️ AI辅助参考，非最终诊断`
- 医疗数据AES-256加密存储 (`~/Desktop/KnowHealth/src/security/encryption.py`)
- 符合HIPAA/GDPR: `~/Desktop/KnowHealth/src/security/compliance.py`
- 医生拥有最终决策权
- 审计日志: `~/Desktop/KnowHealth/src/audit/`

## 参考文件
- iOS客户端: `~/Desktop/KnowHealth-iOS/`
- 后端API: `~/Desktop/KnowHealth/src/`
- 数据库: `~/Desktop/KnowHealth/config/database.yaml`
