# KnowHealth 跨境医疗第二意见平台 - 实施计划

## 项目概述

**产品名**: KnowHealth (医桥)
**定位**: AI驱动的跨境医疗第二意见平台
**差异化**: 数字人+AI降低服务成本, 从"奢侈品"变"可及服务"

---

## 一、能力需求清单 & 解决方案

### 能力矩阵

| # | 能力 | 优先级 | 解决方案 | 来源 |
|---|------|--------|---------|------|
| 1 | AI病历翻译/结构化 | P0 | DrugMind NLP模块 | 复用 |
| 2 | 医学知识库 | P0 | MediChat-RD知识图谱 | 复用 |
| 3 | 数字人交互 | P0 | DigitalSage数字人引擎 | 复用 |
| 4 | 专家匹配算法 | P0 | 自研 (基于病种/地理位置/语言) | 新建 |
| 5 | 视频会诊系统 | P1 | 集成腾讯会议/Zoom SDK | 第三方 |
| 6 | 支付系统 | P1 | Stripe + 支付宝/微信 | 第三方 |
| 7 | 病历安全存储 | P0 | 加密存储 + HIPAA合规 | 新建 |
| 8 | 多语言支持 | P1 | DeepL API + 医学术语库 | 混合 |
| 9 | 用户认证 | P1 | OAuth2 + 手机号验证 | 新建 |
| 10 | 数据分析看板 | P2 | PharmaSim可视化组件 | 复用 |

---

## 二、系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    KnowHealth Platform                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Frontend   │  │  AI Engine   │  │  Digital     │      │
│  │   (React)    │  │  (Python)    │  │  Human       │      │
│  │              │  │              │  │  (DigitalSage)│      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
│  ┌──────┴─────────────────┴─────────────────┴───────┐      │
│  │                  API Gateway                      │      │
│  │              (FastAPI + Auth)                     │      │
│  └──────┬─────────────┬─────────────┬───────────────┘      │
│         │             │             │                       │
│  ┌──────┴──────┐ ┌────┴────┐ ┌─────┴──────┐               │
│  │ Case Service│ │ Payment │ │ Hospital   │               │
│  │ (病例管理)  │ │ (支付)  │ │ Integration│               │
│  └─────────────┘ └─────────┘ └────────────┘               │
│                                                             │
│  ┌─────────────────────────────────────────────────┐       │
│  │              Database Layer                       │       │
│  │  PostgreSQL + Redis + S3 (加密存储)              │       │
│  └─────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、Phase 1: MVP (4-6周)

### 目标
- 支持癌症第二意见的完整流程
- 中→美/日/以色列 单方向
- 10个内测用户验证

### 核心模块

#### 模块1: 患者端 (Patient Portal)
- 注册/登录 (手机号 + OAuth)
- 病历上传 (支持PDF/图片/Word)
- AI病历预处理 & 结构化预览
- 服务选择 & 支付
- 专家意见查看 & 下载
- 消息通知

#### 模块2: AI引擎 (AI Engine)
- 病历OCR + 医学实体提取
- 病历翻译 (中↔英/日)
- 专家匹配推荐
- 数字人预咨询

#### 模块3: 管理后台 (Admin Dashboard)
- 订单管理
- 专家管理
- 病历审核
- 数据统计

#### 模块4: 专家端 (Expert Portal)
- 病例接收 & 审阅
- 意见提交
- 收入统计

---

## 四、技术栈

| 层级 | 技术 | 理由 |
|------|------|------|
| 前端 | React + Next.js | SSR, SEO友好, 生态成熟 |
| UI组件 | Tailwind + shadcn/ui | 快速开发, 专业设计 |
| 后端 | FastAPI (Python) | 与AI模型无缝集成, 高性能 |
| 数据库 | PostgreSQL | 结构化数据, 事务支持 |
| 缓存 | Redis | 会话/消息队列 |
| 文件存储 | S3兼容 (阿里云OSS) | 加密存储, 合规 |
| AI模型 | GPT-4o / Claude | 医学NLP能力最强 |
| OCR | PaddleOCR / Azure | 中文医学文档识别 |
| 视频 | 腾讯会议SDK | 国内可用, 稳定 |
| 支付 | Stripe + 支付宝 | 国际+国内覆盖 |
| 部署 | Docker + K8s | 可扩展 |
| CI/CD | GitHub Actions | 与现有项目一致 |

---

## 五、数据模型

### 核心实体

```sql
-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY,
    phone VARCHAR(20) UNIQUE,
    email VARCHAR(255),
    name VARCHAR(100),
    role ENUM('patient', 'expert', 'admin'),
    language VARCHAR(10) DEFAULT 'zh-CN',
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 病例表
CREATE TABLE cases (
    id UUID PRIMARY KEY,
    patient_id UUID REFERENCES users(id),
    disease_type VARCHAR(100),      -- e.g. 'lung_cancer'
    disease_subtype VARCHAR(100),   -- e.g. 'NSCLC_stage_III'
    status ENUM('pending', 'ai_processing', 'expert_assigned', 
                'opinion_submitted', 'completed', 'cancelled'),
    ai_summary TEXT,                -- AI生成的病历摘要
    structured_data JSONB,          -- 结构化医学数据
    urgency ENUM('normal', 'urgent', 'emergency'),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 病历文件表
CREATE TABLE case_files (
    id UUID PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    file_type ENUM('medical_record', 'lab_report', 'imaging', 'pathology'),
    original_filename VARCHAR(255),
    storage_path VARCHAR(500),      -- S3/OSS路径 (加密)
    ai_extracted_text TEXT,         -- OCR提取文本
    uploaded_at TIMESTAMP
);

-- 专家表
CREATE TABLE experts (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    hospital_id UUID REFERENCES hospitals(id),
    specialties TEXT[],             -- 擅长领域
    languages TEXT[],               -- 支持语言
    credentials JSONB,             -- 资质证明
    rating DECIMAL(3,2),
    total_cases INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE
);

-- 医院表
CREATE TABLE hospitals (
    id UUID PRIMARY KEY,
    name VARCHAR(200),
    name_cn VARCHAR(200),
    country VARCHAR(50),
    city VARCHAR(100),
    specialties TEXT[],
    ranking JSONB,                 -- 各专科排名
    contact_info JSONB
);

-- 专家意见表
CREATE TABLE expert_opinions (
    id UUID PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    expert_id UUID REFERENCES experts(id),
    opinion_text TEXT,
    diagnosis_confirmation TEXT,
    treatment_recommendations TEXT,
    additional_tests TEXT,
    confidence_level ENUM('high', 'medium', 'low'),
    follow_up_needed BOOLEAN,
    submitted_at TIMESTAMP
);

-- 订单表
CREATE TABLE orders (
    id UUID PRIMARY KEY,
    case_id UUID REFERENCES cases(id),
    patient_id UUID REFERENCES users(id),
    service_tier ENUM('basic', 'standard', 'premium'),
    amount DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    payment_status ENUM('pending', 'paid', 'refunded'),
    payment_method VARCHAR(50),
    paid_at TIMESTAMP
);
```

---

## 六、API设计

### 核心端点

```
POST   /api/v1/auth/register          # 用户注册
POST   /api/v1/auth/login             # 登录
POST   /api/v1/auth/verify            # 手机验证

POST   /api/v1/cases                  # 创建病例
GET    /api/v1/cases/:id              # 获取病例详情
POST   /api/v1/cases/:id/files        # 上传病历文件
GET    /api/v1/cases/:id/ai-summary   # 获取AI摘要
POST   /api/v1/cases/:id/submit       # 提交审核

GET    /api/v1/experts                # 专家列表
GET    /api/v1/experts/:id            # 专家详情
POST   /api/v1/experts/match          # AI匹配专家

POST   /api/v1/orders                 # 创建订单
POST   /api/v1/orders/:id/pay         # 支付
GET    /api/v1/orders/:id/status      # 订单状态

GET    /api/v1/opinions/:case_id      # 获取专家意见

POST   /api/v1/ai/ocr                 # OCR识别
POST   /api/v1/ai/translate           # 医学翻译
POST   /api/v1/ai/summarize           # 病历摘要
POST   /api/v1/ai/extract             # 医学实体提取

WS     /api/v1/chat/:case_id          # 数字人对话
WS     /api/v1/video/:session_id      # 视频会诊
```

---

## 七、AI模块详细设计

### 7.1 病历预处理流水线

```
输入: 原始病历文件 (PDF/图片/Word)
  ↓
Step 1: OCR识别 (PaddleOCR)
  ↓
Step 2: 医学实体提取 (GPT-4o)
  - 疾病名称
  - 药物名称
  - 检查指标
  - 时间线
  ↓
Step 3: 结构化整理
  - 诊断信息
  - 治疗历史
  - 检验结果
  ↓
Step 4: 生成摘要
  - 中文摘要
  - 英文摘要 (给专家)
  ↓
输出: 结构化病历 + 双语摘要
```

### 7.2 专家匹配算法

```python
def match_experts(case, available_experts):
    """
    多维度匹配专家
    """
    scores = []
    for expert in available_experts:
        score = 0
        
        # 1. 病种匹配 (权重40%)
        if case.disease_type in expert.specialties:
            score += 40
        if case.disease_subtype in expert.specialties:
            score += 20
            
        # 2. 语言匹配 (权重20%)
        if patient.language in expert.languages:
            score += 20
            
        # 3. 专家评分 (权重15%)
        score += expert.rating * 3  # 0-5分 → 0-15
        
        # 4. 响应速度 (权重10%)
        score += (1 / expert.avg_response_hours) * 10
        
        # 5. 案例经验 (权重15%)
        if expert.total_cases > 100:
            score += 15
        elif expert.total_cases > 50:
            score += 10
        elif expert.total_cases > 20:
            score += 5
            
        scores.append((expert, score))
    
    return sorted(scores, key=lambda x: -x[1])[:3]
```

### 7.3 数字人预咨询

复用DigitalSage的数字人引擎:
- 7x24小时在线
- 收集患者病史
- 回答流程问题
- 安排视频会诊
- 多语言支持

---

## 八、定价模型

| 服务 | 价格 | 包含 |
|------|------|------|
| AI病历分析 | ¥499 | OCR+结构化+摘要+匹配建议 |
| 标准第二意见 | ¥4,999 | 1位专家+书面报告+1次视频 |
| 高级第二意见 | ¥9,999 | 2-3位专家+详细报告+2次视频 |
| VIP全程服务 | ¥29,999 | 专家团+翻译+协调+随访 |
| 年度会员 | ¥99,999 | 无限咨询+优先匹配 |

---

## 九、合规要求

### 必须满足
1. **数据加密**: AES-256存储加密 + TLS传输加密
2. **访问控制**: RBAC权限管理
3. **审计日志**: 所有数据访问记录
4. **数据隔离**: 患者数据严格隔离
5. **隐私政策**: 符合《个人信息保护法》

### 建议满足
1. **HIPAA合规**: 面向美国市场的基础
2. **GDPR合规**: 面向欧洲市场
3. **等保三级**: 国内医疗数据要求

---

## 十、复用现有项目资产

| 资产 | 来源项目 | 复用方式 |
|------|---------|---------|
| 医学NLP模型 | DrugMind | 病历实体提取 |
| 知识图谱 | MediChat-RD | 疾病-专家匹配 |
| 数字人引擎 | DigitalSage | AI预咨询 |
| 可视化组件 | PharmaSim | 数据看板 |
| 支付集成 | 念念-Eterna | 支付流程 |
| GitHub Pages部署 | PharmaSim | 文档站点 |
