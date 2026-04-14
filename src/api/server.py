"""
KnowHealth - AI-Driven Cross-Border Medical Second Opinion Platform
Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import json
import os

# ============================================================
# Configuration
# ============================================================

APP_NAME = "KnowHealth"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "AI驱动的跨境医疗第二意见平台"

# ============================================================
# Enums
# ============================================================

class UserRole(str, Enum):
    PATIENT = "patient"
    EXPERT = "expert"
    ADMIN = "admin"

class CaseStatus(str, Enum):
    PENDING = "pending"
    AI_PROCESSING = "ai_processing"
    EXPERT_ASSIGNED = "expert_assigned"
    OPINION_SUBMITTED = "opinion_submitted"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ServiceTier(str, Enum):
    AI_ANALYSIS = "ai_analysis"           # ¥499
    STANDARD = "standard"                 # ¥4,999
    PREMIUM = "premium"                   # ¥9,999
    VIP = "vip"                          # ¥29,999
    ANNUAL = "annual"                     # ¥99,999

class DiseaseType(str, Enum):
    LUNG_CANCER = "lung_cancer"
    BREAST_CANCER = "breast_cancer"
    COLON_CANCER = "colon_cancer"
    LIVER_CANCER = "liver_cancer"
    GASTRIC_CANCER = "gastric_cancer"
    LEUKEMIA = "leukemia"
    LYMPHOMA = "lymphoma"
    BRAIN_TUMOR = "brain_tumor"
    PANCREATIC_CANCER = "pancreatic_cancer"
    OVARIAN_CANCER = "ovarian_cancer"
    PROSTATE_CANCER = "prostate_cancer"
    RARE_DISEASE = "rare_disease"
    OTHER = "other"

class Urgency(str, Enum):
    NORMAL = "normal"
    URGENT = "urgent"
    EMERGENCY = "emergency"

class FileType(str, Enum):
    MEDICAL_RECORD = "medical_record"
    LAB_REPORT = "lab_report"
    IMAGING = "imaging"
    PATHOLOGY = "pathology"

# ============================================================
# Pydantic Models
# ============================================================

class UserCreate(BaseModel):
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None
    role: UserRole = UserRole.PATIENT
    language: str = "zh-CN"

class UserResponse(BaseModel):
    id: str
    phone: str
    name: str
    email: Optional[str]
    role: UserRole
    language: str
    created_at: datetime

class CaseCreate(BaseModel):
    disease_type: DiseaseType
    disease_subtype: Optional[str] = None
    description: str = Field(..., min_length=10, max_length=5000)
    urgency: Urgency = Urgency.NORMAL
    preferred_countries: List[str] = ["US", "JP", "IL"]
    preferred_languages: List[str] = ["en", "zh"]

class CaseResponse(BaseModel):
    id: str
    patient_id: str
    disease_type: DiseaseType
    disease_subtype: Optional[str]
    status: CaseStatus
    urgency: Urgency
    ai_summary: Optional[str]
    structured_data: Optional[Dict]
    matched_experts: Optional[List[Dict]]
    created_at: datetime
    updated_at: datetime

class ExpertOpinion(BaseModel):
    diagnosis_confirmation: str
    treatment_recommendations: str
    additional_tests: Optional[str] = None
    confidence_level: str = Field(..., pattern=r'^(high|medium|low)$')
    follow_up_needed: bool = False
    opinion_text: str

class OrderCreate(BaseModel):
    case_id: str
    service_tier: ServiceTier

class OrderResponse(BaseModel):
    id: str
    case_id: str
    service_tier: ServiceTier
    amount: float
    currency: str
    payment_status: str
    created_at: datetime

class AISummaryRequest(BaseModel):
    case_id: str
    language: str = "en"

class ExpertMatchRequest(BaseModel):
    case_id: str
    top_n: int = Field(default=3, ge=1, le=10)

# ============================================================
# In-Memory Storage (Replace with PostgreSQL in production)
# ============================================================

users_db: Dict[str, Dict] = {}
cases_db: Dict[str, Dict] = {}
files_db: Dict[str, List[Dict]] = {}
experts_db: Dict[str, Dict] = {}
opinions_db: Dict[str, Dict] = {}
orders_db: Dict[str, Dict] = {}

# Service pricing
SERVICE_PRICING = {
    ServiceTier.AI_ANALYSIS: {"amount": 499, "currency": "CNY"},
    ServiceTier.STANDARD: {"amount": 4999, "currency": "CNY"},
    ServiceTier.PREMIUM: {"amount": 9999, "currency": "CNY"},
    ServiceTier.VIP: {"amount": 29999, "currency": "CNY"},
    ServiceTier.ANNUAL: {"amount": 99999, "currency": "CNY"},
}

# ============================================================
# Sample Expert Data
# ============================================================

SAMPLE_EXPERTS = [
    {
        "id": "exp_001",
        "name": "Dr. James Wilson",
        "name_cn": "James Wilson 博士",
        "hospital": "Mayo Clinic",
        "hospital_cn": "梅奥诊所",
        "country": "US",
        "specialties": ["lung_cancer", "breast_cancer", "colon_cancer"],
        "languages": ["en"],
        "credentials": {"title": "Oncology Chief", "years": 25},
        "rating": 4.9,
        "total_cases": 342,
        "avg_response_hours": 48,
        "bio": "Board-certified oncologist with 25 years of experience in solid tumor treatment."
    },
    {
        "id": "exp_002",
        "name": "Dr. Yuki Tanaka",
        "name_cn": "田中由纪博士",
        "hospital": "National Cancer Center Japan",
        "hospital_cn": "日本国立癌症中心",
        "country": "JP",
        "specialties": ["gastric_cancer", "liver_cancer", "pancreatic_cancer"],
        "languages": ["ja", "en"],
        "credentials": {"title": "Surgical Oncology Director", "years": 20},
        "rating": 4.8,
        "total_cases": 278,
        "avg_response_hours": 36,
        "bio": "Leading expert in gastrointestinal cancer surgery with pioneering minimally invasive techniques."
    },
    {
        "id": "exp_003",
        "name": "Dr. Rachel Cohen",
        "name_cn": "Rachel Cohen 博士",
        "hospital": "Sheba Medical Center",
        "hospital_cn": "谢巴医疗中心",
        "country": "IL",
        "specialties": ["rare_disease", "leukemia", "lymphoma"],
        "languages": ["en", "he"],
        "credentials": {"title": "Rare Disease Research Lead", "years": 18},
        "rating": 4.95,
        "total_cases": 156,
        "avg_response_hours": 24,
        "bio": "World-renowned expert in rare hematological diseases and precision medicine."
    },
    {
        "id": "exp_004",
        "name": "Dr. Michael Chen",
        "name_cn": "陈明博士",
        "hospital": "Cleveland Clinic",
        "hospital_cn": "克利夫兰诊所",
        "country": "US",
        "specialties": ["brain_tumor", "lung_cancer"],
        "languages": ["en", "zh"],
        "credentials": {"title": "Neurosurgery Attending", "years": 15},
        "rating": 4.85,
        "total_cases": 198,
        "avg_response_hours": 40,
        "bio": "Specialized in complex brain tumor surgery with awake craniotomy expertise. Bilingual Chinese-English."
    },
    {
        "id": "exp_005",
        "name": "Dr. Sarah Park",
        "name_cn": "朴智妍博士",
        "hospital": "Samsung Medical Center",
        "hospital_cn": "三星医疗中心",
        "country": "KR",
        "specialties": ["breast_cancer", "ovarian_cancer"],
        "languages": ["ko", "en"],
        "credentials": {"title": "Breast Cancer Center Director", "years": 22},
        "rating": 4.92,
        "total_cases": 412,
        "avg_response_hours": 30,
        "bio": "Leading breast cancer specialist with extensive experience in targeted therapy and immunotherapy."
    },
]

# Initialize experts
for exp in SAMPLE_EXPERTS:
    experts_db[exp["id"]] = exp

# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

# ============================================================
# Helper Functions
# ============================================================

def generate_id() -> str:
    return str(uuid.uuid4())[:12]

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials:
        raise HTTPException(status_code=401, detail="未登录")
    token = credentials.credentials
    # Simple token lookup (in production, use JWT)
    for user in users_db.values():
        if user.get("token") == token:
            return user
    raise HTTPException(status_code=401, detail="无效的凭证")

def match_experts_for_case(case: Dict, top_n: int = 3) -> List[Dict]:
    """Match experts based on disease type, language, and ratings."""
    scores = []
    for expert in experts_db.values():
        score = 0
        
        # Disease match (40%)
        if case.get("disease_type") in expert["specialties"]:
            score += 40
        if case.get("disease_subtype") in expert.get("specialties", []):
            score += 20
        
        # Language match (20%)
        patient_langs = case.get("preferred_languages", ["en", "zh"])
        for lang in patient_langs:
            if lang in expert["languages"]:
                score += 10
        
        # Rating (15%)
        score += expert["rating"] * 3
        
        # Response speed (10%)
        if expert["avg_response_hours"] <= 24:
            score += 10
        elif expert["avg_response_hours"] <= 48:
            score += 7
        else:
            score += 4
        
        # Experience (15%)
        if expert["total_cases"] > 300:
            score += 15
        elif expert["total_cases"] > 200:
            score += 12
        elif expert["total_cases"] > 100:
            score += 8
        else:
            score += 4
        
        scores.append({
            "expert": expert,
            "score": round(score, 1),
            "match_reasons": []
        })
    
    # Sort by score
    scores.sort(key=lambda x: -x["score"])
    return scores[:top_n]

# ============================================================
# API Routes - Health Check
# ============================================================

@app.get("/")
async def root():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "users": len(users_db),
        "cases": len(cases_db),
        "experts": len(experts_db),
        "timestamp": datetime.now().isoformat()
    }

# ============================================================
# API Routes - Authentication
# ============================================================

@app.post("/api/v1/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user."""
    # Check if phone already exists
    for user in users_db.values():
        if user["phone"] == user_data.phone:
            raise HTTPException(status_code=400, detail="该手机号已注册")
    
    user_id = generate_id()
    user = {
        "id": user_id,
        "phone": user_data.phone,
        "name": user_data.name,
        "email": user_data.email,
        "role": user_data.role.value,
        "language": user_data.language,
        "token": f"kh_{generate_id()}",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    users_db[user_id] = user
    
    return UserResponse(
        id=user_id,
        phone=user["phone"],
        name=user["name"],
        email=user["email"],
        role=user["role"],
        language=user["language"],
        created_at=user["created_at"]
    )

@app.post("/api/v1/auth/login")
async def login(phone: str = Form(...)):
    """Login with phone number."""
    for user in users_db.values():
        if user["phone"] == phone:
            return {
                "token": user["token"],
                "user_id": user["id"],
                "name": user["name"],
                "role": user["role"]
            }
    raise HTTPException(status_code=404, detail="用户不存在")

# ============================================================
# API Routes - Cases
# ============================================================

@app.post("/api/v1/cases", response_model=CaseResponse)
async def create_case(case_data: CaseCreate, user: Dict = Depends(get_current_user)):
    """Create a new medical case for second opinion."""
    if user["role"] != "patient":
        raise HTTPException(status_code=403, detail="只有患者可以创建病例")
    
    case_id = generate_id()
    case = {
        "id": case_id,
        "patient_id": user["id"],
        "disease_type": case_data.disease_type.value,
        "disease_subtype": case_data.disease_subtype,
        "description": case_data.description,
        "status": CaseStatus.PENDING.value,
        "urgency": case_data.urgency.value,
        "preferred_countries": case_data.preferred_countries,
        "preferred_languages": case_data.preferred_languages,
        "ai_summary": None,
        "structured_data": None,
        "matched_experts": None,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    cases_db[case_id] = case
    files_db[case_id] = []
    
    return CaseResponse(**case)

@app.get("/api/v1/cases/{case_id}", response_model=CaseResponse)
async def get_case(case_id: str, user: Dict = Depends(get_current_user)):
    """Get case details."""
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="病例不存在")
    
    case = cases_db[case_id]
    # Check permission
    if user["role"] == "patient" and case["patient_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="无权查看此病例")
    
    return CaseResponse(**case)

@app.get("/api/v1/cases")
async def list_cases(
    status: Optional[CaseStatus] = None,
    user: Dict = Depends(get_current_user)
):
    """List cases for current user."""
    result = []
    for case in cases_db.values():
        if user["role"] == "patient" and case["patient_id"] != user["id"]:
            continue
        if status and case["status"] != status.value:
            continue
        result.append(case)
    
    return {
        "total": len(result),
        "cases": result
    }

@app.post("/api/v1/cases/{case_id}/files")
async def upload_file(
    case_id: str,
    file: UploadFile = File(...),
    file_type: FileType = Form(FileType.MEDICAL_RECORD),
    user: Dict = Depends(get_current_user)
):
    """Upload a medical file to a case."""
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="病例不存在")
    
    case = cases_db[case_id]
    if case["patient_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="无权上传到此病例")
    
    file_id = generate_id()
    file_record = {
        "id": file_id,
        "case_id": case_id,
        "file_type": file_type.value,
        "original_filename": file.filename,
        "content_type": file.content_type,
        "size": 0,  # Would be set after saving
        "uploaded_at": datetime.now()
    }
    
    files_db[case_id].append(file_record)
    
    # Update case status
    case["status"] = CaseStatus.AI_PROCESSING.value
    case["updated_at"] = datetime.now()
    
    return {
        "file_id": file_id,
        "filename": file.filename,
        "status": "uploaded",
        "message": "文件已上传，AI正在处理中..."
    }

# ============================================================
# API Routes - AI Services
# ============================================================

@app.post("/api/v1/ai/summarize")
async def ai_summarize(request: AISummaryRequest, user: Dict = Depends(get_current_user)):
    """Generate AI summary for a case."""
    if request.case_id not in cases_db:
        raise HTTPException(status_code=404, detail="病例不存在")
    
    case = cases_db[request.case_id]
    
    # Simulate AI processing (in production, call GPT-4o)
    ai_summary_en = f"""
AI-Generated Medical Summary
============================

Patient Case: {case['disease_type'].replace('_', ' ').title()}

Key Findings:
- Primary diagnosis: {case['disease_type'].replace('_', ' ').title()}
- Stage/Subtype: {case.get('disease_subtype', 'To be determined')}
- Urgency Level: {case['urgency']}

Clinical Description:
{case.get('description', 'No description provided')[:500]}

Recommended Expert Matching:
Based on the case profile, we recommend experts specializing in {case['disease_type'].replace('_', ' ')} 
from top-tier hospitals in {', '.join(case.get('preferred_countries', ['US']))}.

Files Uploaded: {len(files_db.get(request.case_id, []))} document(s)
"""

    ai_summary_zh = f"""
AI生成的病历摘要
================

患者病例: {case['disease_type'].replace('_', ' ').title()}

主要发现:
- 初步诊断: {case['disease_type'].replace('_', ' ').title()}
- 分期/亚型: {case.get('disease_subtype', '待确定')}
- 紧急程度: {case['urgency']}

临床描述:
{case.get('description', '未提供描述')[:500]}

推荐专家匹配:
根据病例概况,我们推荐来自{', '.join(case.get('preferred_countries', ['美国']))}顶级医院的
{case['disease_type'].replace('_', ' ')}领域专家。

已上传文件: {len(files_db.get(request.case_id, []))} 份
"""

    # Update case
    case["ai_summary"] = ai_summary_en if request.language == "en" else ai_summary_zh
    case["structured_data"] = {
        "disease_type": case["disease_type"],
        "disease_subtype": case.get("disease_subtype"),
        "urgency": case["urgency"],
        "key_terms": [
            case["disease_type"].replace("_", " "),
            "second opinion",
            "跨境医疗"
        ],
        "processing_timestamp": datetime.now().isoformat()
    }
    case["updated_at"] = datetime.now()
    
    return {
        "case_id": request.case_id,
        "language": request.language,
        "summary": case["ai_summary"],
        "structured_data": case["structured_data"]
    }

@app.post("/api/v1/experts/match")
async def match_experts(request: ExpertMatchRequest, user: Dict = Depends(get_current_user)):
    """Match experts for a case."""
    if request.case_id not in cases_db:
        raise HTTPException(status_code=404, detail="病例不存在")
    
    case = cases_db[request.case_id]
    matches = match_experts_for_case(case, request.top_n)
    
    # Update case
    case["matched_experts"] = [m["expert"]["id"] for m in matches]
    case["status"] = CaseStatus.EXPERT_ASSIGNED.value
    case["updated_at"] = datetime.now()
    
    return {
        "case_id": request.case_id,
        "matched_experts": matches,
        "total": len(matches)
    }

# ============================================================
# API Routes - Experts
# ============================================================

@app.get("/api/v1/experts")
async def list_experts(
    specialty: Optional[str] = None,
    country: Optional[str] = None,
    language: Optional[str] = None
):
    """List available experts with filters."""
    result = []
    for expert in experts_db.values():
        if specialty and specialty not in expert["specialties"]:
            continue
        if country and expert["country"] != country:
            continue
        if language and language not in expert["languages"]:
            continue
        result.append(expert)
    
    return {
        "total": len(result),
        "experts": result
    }

@app.get("/api/v1/experts/{expert_id}")
async def get_expert(expert_id: str):
    """Get expert details."""
    if expert_id not in experts_db:
        raise HTTPException(status_code=404, detail="专家不存在")
    return experts_db[expert_id]

# ============================================================
# API Routes - Orders & Payment
# ============================================================

@app.post("/api/v1/orders", response_model=OrderResponse)
async def create_order(order_data: OrderCreate, user: Dict = Depends(get_current_user)):
    """Create a new order."""
    if order_data.case_id not in cases_db:
        raise HTTPException(status_code=404, detail="病例不存在")
    
    pricing = SERVICE_PRICING[order_data.service_tier]
    order_id = generate_id()
    
    order = {
        "id": order_id,
        "case_id": order_data.case_id,
        "patient_id": user["id"],
        "service_tier": order_data.service_tier.value,
        "amount": pricing["amount"],
        "currency": pricing["currency"],
        "payment_status": "pending",
        "created_at": datetime.now()
    }
    orders_db[order_id] = order
    
    return OrderResponse(**order)

@app.post("/api/v1/orders/{order_id}/pay")
async def process_payment(order_id: str, user: Dict = Depends(get_current_user)):
    """Process payment for an order."""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="订单不存在")
    
    order = orders_db[order_id]
    if order["payment_status"] == "paid":
        raise HTTPException(status_code=400, detail="订单已支付")
    
    # Simulate payment processing
    order["payment_status"] = "paid"
    order["paid_at"] = datetime.now()
    
    return {
        "order_id": order_id,
        "status": "paid",
        "amount": order["amount"],
        "currency": order["currency"],
        "message": "支付成功！专家将在24-48小时内审核您的病例。"
    }

# ============================================================
# API Routes - Opinions
# ============================================================

@app.get("/api/v1/opinions/{case_id}")
async def get_opinion(case_id: str, user: Dict = Depends(get_current_user)):
    """Get expert opinion for a case."""
    if case_id not in cases_db:
        raise HTTPException(status_code=404, detail="病例不存在")
    
    # Simulate expert opinion
    case = cases_db[case_id]
    
    return {
        "case_id": case_id,
        "status": case["status"],
        "opinion": {
            "expert_name": "Dr. James Wilson",
            "hospital": "Mayo Clinic",
            "diagnosis_confirmation": f"Based on the provided medical records, I confirm the diagnosis of {case['disease_type'].replace('_', ' ')}.",
            "treatment_recommendations": "1. Consider targeted therapy based on molecular profiling.\n2. Immunotherapy may be beneficial.\n3. Regular monitoring with imaging every 3 months.",
            "additional_tests": "Recommend comprehensive genomic profiling (NGS panel) to identify potential targeted therapy options.",
            "confidence_level": "high",
            "follow_up_needed": True,
            "submitted_at": datetime.now().isoformat()
        }
    }

# ============================================================
# API Routes - Statistics (Admin)
# ============================================================

@app.get("/api/v1/stats")
async def get_stats():
    """Get platform statistics."""
    return {
        "total_users": len(users_db),
        "total_cases": len(cases_db),
        "total_experts": len(experts_db),
        "total_orders": len(orders_db),
        "total_revenue": sum(o["amount"] for o in orders_db.values() if o["payment_status"] == "paid"),
        "cases_by_status": {
            status.value: sum(1 for c in cases_db.values() if c["status"] == status.value)
            for status in CaseStatus
        },
        "cases_by_disease": {
            disease.value: sum(1 for c in cases_db.values() if c["disease_type"] == disease.value)
            for disease in DiseaseType
        }
    }

# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
