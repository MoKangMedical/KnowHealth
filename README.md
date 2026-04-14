# KnowHealth - AI驱动的跨境医疗第二意见平台

> 让全球最好的医疗决策触手可及

## 🏥 项目概述

KnowHealth 是一个 AI 驱动的跨境医疗第二意见平台，利用 AI 技术让患者能够便捷地获取全球顶级医疗专家的第二意见。

### 核心价值

- **AI赋能**: 自动翻译、结构化、摘要病历
- **全球专家**: 梅奥诊所、克利夫兰诊所、谢巴医疗中心等
- **数字人**: 7×24 AI医疗助手预咨询
- **可及性**: 比传统服务便宜50%+

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python src/api/server.py

# 访问
# API: http://localhost:8080
# 文档: http://localhost:8080/docs
# 前端: open src/frontend/index.html
```

## 📁 项目结构

```
KnowHealth/
├── docs/                    # 文档
│   └── IMPLEMENTATION_PLAN.md
├── src/
│   ├── api/                 # 后端 API
│   │   ├── server.py        # FastAPI 主应用
│   │   ├── routes/          # API 路由
│   │   ├── services/        # 业务逻辑
│   │   └── models/          # 数据模型
│   ├── ai/                  # AI 引擎
│   │   ├── engine.py        # NLP + 专家匹配
│   │   ├── agents/          # AI Agent
│   │   └── prompts/         # 提示词模板
│   ├── frontend/            # 前端
│   │   ├── index.html       # 首页
│   │   ├── pages/           # 页面
│   │   ├── components/      # 组件
│   │   └── styles/          # 样式
│   └── integrations/        # 第三方集成
│       ├── hospitals/       # 医院对接
│       └── translators/     # 翻译服务
├── config/                  # 配置
├── scripts/                 # 脚本
├── tests/                   # 测试
├── .env                     # 环境变量
└── requirements.txt         # Python 依赖
```

## 🔌 API 端点

### 认证
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 登录

### 病例
- `POST /api/v1/cases` - 创建病例
- `GET /api/v1/cases/:id` - 获取病例详情
- `POST /api/v1/cases/:id/files` - 上传病历文件

### AI 服务
- `POST /api/v1/ai/summarize` - AI病历摘要
- `POST /api/v1/experts/match` - 专家匹配

### 订单 & 支付
- `POST /api/v1/orders` - 创建订单
- `POST /api/v1/orders/:id/pay` - 支付

### 专家意见
- `GET /api/v1/opinions/:case_id` - 获取专家意见

## 💰 定价

| 服务 | 价格 | 包含 |
|------|------|------|
| AI病历分析 | ¥499 | OCR+结构化+摘要+匹配建议 |
| 标准第二意见 | ¥4,999 | 1位专家+书面报告+1次视频 |
| 高级多学科 | ¥9,999 | 2-3位专家+详细报告+2次视频 |
| VIP全程服务 | ¥29,999 | 专家团+翻译+协调+随访 |
| 年度会员 | ¥99,999/年 | 无限咨询+优先匹配 |

## 🏗️ 技术栈

- **后端**: FastAPI (Python)
- **前端**: HTML + Tailwind CSS + Alpine.js
- **AI**: OpenAI GPT-4o (病历NLP)
- **翻译**: DeepL API (医学翻译)
- **OCR**: PaddleOCR (病历识别)
- **存储**: PostgreSQL + Redis + S3
- **支付**: Stripe + 支付宝/微信

## 🔒 合规

- 端到端加密 (AES-256 + TLS 1.3)
- HIPAA 合规
- GDPR 合规
- 《个人信息保护法》合规
- 完整审计日志

## 📈 路线图

### Phase 1: MVP (当前)
- [x] 后端API框架
- [x] AI病历处理引擎
- [x] 专家匹配算法
- [x] 数字人预咨询
- [x] 订单支付流程
- [x] 前端首页

### Phase 2: 扩展
- [ ] 数据库集成 (PostgreSQL)
- [ ] 视频会诊集成
- [ ] 移动端适配
- [ ] 多语言支持扩展

### Phase 3: B2B
- [ ] 企业/保险合作方案
- [ ] 医院系统对接
- [ ] 数据分析看板

## 🤝 合作伙伴

- 梅奥诊所 (Mayo Clinic)
- 克利夫兰诊所 (Cleveland Clinic)
- 谢巴医疗中心 (Sheba Medical Center)
- 日本国立癌症中心
- 三星医疗中心

## 📞 联系

- 邮箱: contact@knowhealth.ai
- 电话: 400-888-KNOW
- 地址: 上海 · 北京 · 纽约
