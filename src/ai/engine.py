"""
KnowHealth AI Engine
Medical NLP, Expert Matching, and Digital Human Integration
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


# ============================================================
# Medical Entity Types
# ============================================================

class MedicalEntityType(Enum):
    DISEASE = "disease"
    DRUG = "drug"
    SYMPTOM = "symptom"
    PROCEDURE = "procedure"
    TEST = "test"
    BODY_PART = "body_part"
    GENE = "gene"
    STAGE = "stage"


@dataclass
class MedicalEntity:
    text: str
    entity_type: MedicalEntityType
    confidence: float
    start_pos: int
    end_pos: int
    normalized: str  # Standardized name


@dataclass
class PatientTimeline:
    events: List[Dict]
    diagnosis_date: Optional[str]
    treatment_phases: List[Dict]


@dataclass
class StructuredMedicalRecord:
    patient_id: str
    demographics: Dict
    chief_complaint: str
    diagnosis: List[Dict]
    medical_history: List[Dict]
    medications: List[Dict]
    lab_results: List[Dict]
    imaging_results: List[Dict]
    treatment_history: List[Dict]
    timeline: PatientTimeline
    entities: List[MedicalEntity]
    summary_cn: str
    summary_en: str
    confidence_score: float


# ============================================================
# Medical NLP Engine
# ============================================================

class MedicalNLPEngine:
    """
    AI-powered medical text processing engine.
    In production, this would call GPT-4o or similar models.
    """
    
    # Disease keyword patterns
    DISEASE_PATTERNS = {
        "lung_cancer": ["肺癌", "肺腺癌", "肺鳞癌", "小细胞肺癌", "NSCLC", "SCLC", "lung cancer", "lung adenocarcinoma"],
        "breast_cancer": ["乳腺癌", "breast cancer", "乳腺肿瘤"],
        "colon_cancer": ["结肠癌", "直肠癌", "结直肠癌", "colon cancer", "colorectal cancer"],
        "liver_cancer": ["肝癌", "肝细胞癌", "liver cancer", "hepatocellular carcinoma", "HCC"],
        "gastric_cancer": ["胃癌", "gastric cancer", "stomach cancer"],
        "leukemia": ["白血病", "leukemia", "ALL", "AML", "CLL", "CML"],
        "lymphoma": ["淋巴瘤", "lymphoma", "霍奇金", "Hodgkin", "非霍奇金", "NHL"],
        "brain_tumor": ["脑肿瘤", "脑瘤", "glioma", "glioblastoma", "brain tumor", "meningioma"],
        "pancreatic_cancer": ["胰腺癌", "pancreatic cancer"],
        "ovarian_cancer": ["卵巢癌", "ovarian cancer"],
        "prostate_cancer": ["前列腺癌", "prostate cancer"],
    }
    
    # Stage patterns
    STAGE_PATTERNS = [
        r'(?:第|Stage\s*)?([I1-4一二三四期]+)\s*(?:期|期|stage)',
        r'(?:TNM|tnm)[:\s]*([Tt][0-4][Nn][0-3][Mm][0-1])',
        r'([A-Da-d])\s*(?:期|期|stage)',
    ]
    
    # Common drug names
    DRUG_PATTERNS = {
        "targeted_therapy": ["吉非替尼", "厄洛替尼", "奥希替尼", "gefitinib", "erlotinib", "osimertinib", "阿来替尼", "alectinib"],
        "immunotherapy": ["帕博利珠", "纳武利尤", "pembrolizumab", "nivolumab", "K药", "O药", "PD-1", "PD-L1"],
        "chemotherapy": ["顺铂", "卡铂", "紫杉醇", "培美曲塞", "cisplatin", "carboplatin", "paclitaxel", "pemetrexed"],
    }
    
    # Lab test patterns
    LAB_PATTERNS = {
        "tumor_markers": ["CEA", "CA125", "CA19-9", "AFP", "PSA", "NSE", "CYFRA21-1"],
        "blood_count": ["WBC", "RBC", "HGB", "PLT", "白细胞", "红细胞", "血红蛋白", "血小板"],
        "liver_function": ["ALT", "AST", "ALP", "GGT", "总胆红素", "白蛋白"],
        "kidney_function": ["肌酐", "尿素氮", "creatinine", "BUN", "GFR"],
    }
    
    def __init__(self):
        """Initialize the NLP engine."""
        self.processed_cases = 0
    
    def extract_entities(self, text: str) -> List[MedicalEntity]:
        """
        Extract medical entities from text.
        """
        entities = []
        
        # Extract diseases
        for disease_type, keywords in self.DISEASE_PATTERNS.items():
            for keyword in keywords:
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                for match in pattern.finditer(text):
                    entities.append(MedicalEntity(
                        text=match.group(),
                        entity_type=MedicalEntityType.DISEASE,
                        confidence=0.95,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        normalized=disease_type
                    ))
        
        # Extract stages
        for pattern in self.STAGE_PATTERNS:
            regex = re.compile(pattern, re.IGNORECASE)
            for match in regex.finditer(text):
                entities.append(MedicalEntity(
                    text=match.group(),
                    entity_type=MedicalEntityType.STAGE,
                    confidence=0.9,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    normalized=match.group(1).upper()
                ))
        
        # Extract drugs
        for drug_type, drugs in self.DRUG_PATTERNS.items():
            for drug in drugs:
                pattern = re.compile(re.escape(drug), re.IGNORECASE)
                for match in pattern.finditer(text):
                    entities.append(MedicalEntity(
                        text=match.group(),
                        entity_type=MedicalEntityType.DRUG,
                        confidence=0.9,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        normalized=f"{drug_type}:{drug}"
                    ))
        
        # Extract lab tests
        for test_type, tests in self.LAB_PATTERNS.items():
            for test in tests:
                pattern = re.compile(re.escape(test), re.IGNORECASE)
                for match in pattern.finditer(text):
                    entities.append(MedicalEntity(
                        text=match.group(),
                        entity_type=MedicalEntityType.TEST,
                        confidence=0.85,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        normalized=f"{test_type}:{test}"
                    ))
        
        # Remove duplicates
        seen = set()
        unique_entities = []
        for e in entities:
            key = (e.text.lower(), e.start_pos)
            if key not in seen:
                seen.add(key)
                unique_entities.append(e)
        
        return sorted(unique_entities, key=lambda x: x.start_pos)
    
    def identify_disease(self, text: str) -> Tuple[Optional[str], Optional[str], float]:
        """
        Identify primary disease and subtype from text.
        Returns (disease_type, subtype, confidence)
        """
        entities = self.extract_entities(text)
        diseases = [e for e in entities if e.entity_type == MedicalEntityType.DISEASE]
        stages = [e for e in entities if e.entity_type == MedicalEntityType.STAGE]
        
        if not diseases:
            return None, None, 0.0
        
        # Most frequently mentioned disease
        disease_counts = {}
        for d in diseases:
            disease_counts[d.normalized] = disease_counts.get(d.normalized, 0) + 1
        
        primary_disease = max(disease_counts, key=disease_counts.get)
        stage = stages[0].normalized if stages else None
        
        confidence = min(0.95, 0.7 + (len(diseases) * 0.05))
        
        return primary_disease, stage, confidence
    
    def generate_structured_record(self, text: str, patient_id: str) -> StructuredMedicalRecord:
        """
        Generate a structured medical record from raw text.
        """
        entities = self.extract_entities(text)
        disease_type, stage, confidence = self.identify_disease(text)
        
        # Extract medications
        medications = []
        drug_entities = [e for e in entities if e.entity_type == MedicalEntityType.DRUG]
        for de in drug_entities:
            medications.append({
                "name": de.text,
                "category": de.normalized.split(":")[0],
                "confidence": de.confidence
            })
        
        # Extract lab results
        lab_results = []
        test_entities = [e for e in entities if e.entity_type == MedicalEntityType.TEST]
        for te in test_entities:
            lab_results.append({
                "test_name": te.text,
                "category": te.normalized.split(":")[0],
                "confidence": te.confidence
            })
        
        # Generate summaries
        summary_cn = self._generate_summary_cn(disease_type, stage, medications, lab_results, text)
        summary_en = self._generate_summary_en(disease_type, stage, medications, lab_results, text)
        
        record = StructuredMedicalRecord(
            patient_id=patient_id,
            demographics={},
            chief_complaint=text[:200],
            diagnosis=[{
                "disease": disease_type,
                "stage": stage,
                "confidence": confidence
            }] if disease_type else [],
            medical_history=[],
            medications=medications,
            lab_results=lab_results,
            imaging_results=[],
            treatment_history=[],
            timeline=PatientTimeline(
                events=[],
                diagnosis_date=None,
                treatment_phases=[]
            ),
            entities=entities,
            summary_cn=summary_cn,
            summary_en=summary_en,
            confidence_score=confidence
        )
        
        self.processed_cases += 1
        return record
    
    def _generate_summary_cn(self, disease, stage, medications, lab_results, original_text):
        """Generate Chinese summary."""
        parts = ["【AI病历摘要】\n"]
        
        if disease:
            disease_display = disease.replace("_", " ").replace("cancer", "癌").title()
            parts.append(f"诊断: {disease_display}")
            if stage:
                parts.append(f"分期: {stage}期")
        
        if medications:
            drug_names = [m["name"] for m in medications]
            parts.append(f"用药: {', '.join(drug_names)}")
        
        if lab_results:
            test_names = [l["test_name"] for l in lab_results]
            parts.append(f"相关检查: {', '.join(test_names)}")
        
        parts.append(f"\n原文摘要: {original_text[:300]}...")
        parts.append("\n[此摘要由AI自动生成，仅供参考]")
        
        return "\n".join(parts)
    
    def _generate_summary_en(self, disease, stage, medications, lab_results, original_text):
        """Generate English summary."""
        parts = ["[AI-Generated Medical Summary]\n"]
        
        if disease:
            disease_display = disease.replace("_", " ").title()
            parts.append(f"Diagnosis: {disease_display}")
            if stage:
                parts.append(f"Stage: {stage}")
        
        if medications:
            drug_names = [m["name"] for m in medications]
            parts.append(f"Medications: {', '.join(drug_names)}")
        
        if lab_results:
            test_names = [l["test_name"] for l in lab_results]
            parts.append(f"Relevant Tests: {', '.join(test_names)}")
        
        parts.append(f"\nExcerpt: {original_text[:300]}...")
        parts.append("\n[This summary is AI-generated and for reference only]")
        
        return "\n".join(parts)
    
    def translate_medical_text(self, text: str, target_lang: str = "en") -> str:
        """
        Translate medical text with proper terminology.
        In production, this would use DeepL API + medical dictionary.
        """
        # Simplified translation mapping
        medical_terms = {
            "肺癌": "lung cancer",
            "乳腺癌": "breast cancer",
            "化疗": "chemotherapy",
            "靶向治疗": "targeted therapy",
            "免疫治疗": "immunotherapy",
            "手术": "surgery",
            "放疗": "radiation therapy",
            "转移": "metastasis",
            "复发": "recurrence",
            "预后": "prognosis",
        }
        
        if target_lang == "en":
            result = text
            for cn, en in medical_terms.items():
                result = result.replace(cn, en)
            return result
        else:
            return text  # Return as-is for Chinese


# ============================================================
# Expert Matching Engine
# ============================================================

@dataclass
class ExpertProfile:
    id: str
    name: str
    hospital: str
    country: str
    specialties: List[str]
    languages: List[str]
    rating: float
    total_cases: int
    avg_response_hours: int
    certifications: List[str]


class ExpertMatchingEngine:
    """
    Match patients with the most suitable experts.
    """
    
    def __init__(self):
        self.experts = self._load_experts()
    
    def _load_experts(self) -> List[ExpertProfile]:
        """Load expert database."""
        return [
            ExpertProfile(
                id="exp_001",
                name="Dr. James Wilson",
                hospital="Mayo Clinic",
                country="US",
                specialties=["lung_cancer", "breast_cancer", "colon_cancer"],
                languages=["en"],
                rating=4.9,
                total_cases=342,
                avg_response_hours=48,
                certifications=["Board Certified Oncology", "ASCO Member"]
            ),
            ExpertProfile(
                id="exp_002",
                name="Dr. Yuki Tanaka",
                hospital="National Cancer Center Japan",
                country="JP",
                specialties=["gastric_cancer", "liver_cancer", "pancreatic_cancer"],
                languages=["ja", "en"],
                rating=4.8,
                total_cases=278,
                avg_response_hours=36,
                certifications=["JSCO Board Certified"]
            ),
            ExpertProfile(
                id="exp_003",
                name="Dr. Rachel Cohen",
                hospital="Sheba Medical Center",
                country="IL",
                specialties=["rare_disease", "leukemia", "lymphoma"],
                languages=["en", "he"],
                rating=4.95,
                total_cases=156,
                avg_response_hours=24,
                certifications=["ESH Board Certified"]
            ),
            ExpertProfile(
                id="exp_004",
                name="Dr. Michael Chen",
                hospital="Cleveland Clinic",
                country="US",
                specialties=["brain_tumor", "lung_cancer"],
                languages=["en", "zh"],
                rating=4.85,
                total_cases=198,
                avg_response_hours=40,
                certifications=["AANS Board Certified"]
            ),
            ExpertProfile(
                id="exp_005",
                name="Dr. Sarah Park",
                hospital="Samsung Medical Center",
                country="KR",
                specialties=["breast_cancer", "ovarian_cancer"],
                languages=["ko", "en"],
                rating=4.92,
                total_cases=412,
                avg_response_hours=30,
                certifications=["KBCS Board Certified"]
            ),
        ]
    
    def match(
        self,
        disease_type: str,
        preferred_countries: List[str] = None,
        preferred_languages: List[str] = None,
        urgency: str = "normal",
        top_n: int = 3
    ) -> List[Dict]:
        """
        Match experts based on multiple criteria.
        """
        scored_experts = []
        
        for expert in self.experts:
            score = 0
            reasons = []
            
            # Disease match (40 points max)
            if disease_type in expert.specialties:
                score += 40
                reasons.append(f"擅长{disease_type.replace('_', ' ')}")
            
            # Country preference (15 points max)
            if preferred_countries and expert.country in preferred_countries:
                score += 15
                reasons.append(f"位于优选国家{expert.country}")
            
            # Language match (20 points max)
            if preferred_languages:
                lang_matches = len(set(preferred_languages) & set(expert.languages))
                lang_score = min(20, lang_matches * 10)
                score += lang_score
                if lang_matches > 0:
                    reasons.append("语言匹配")
            
            # Rating (15 points max)
            rating_score = expert.rating * 3
            score += rating_score
            
            # Response time (10 points max)
            if urgency == "emergency":
                if expert.avg_response_hours <= 24:
                    score += 10
                    reasons.append("可紧急响应")
            elif urgency == "urgent":
                if expert.avg_response_hours <= 48:
                    score += 8
            else:
                if expert.avg_response_hours <= 48:
                    score += 7
                elif expert.avg_response_hours <= 72:
                    score += 4
            
            # Experience bonus (up to 5 extra points)
            if expert.total_cases > 300:
                score += 5
            elif expert.total_cases > 200:
                score += 3
            
            scored_experts.append({
                "expert": asdict(expert),
                "score": round(score, 1),
                "match_reasons": reasons
            })
        
        # Sort by score descending
        scored_experts.sort(key=lambda x: -x["score"])
        
        return scored_experts[:top_n]


# ============================================================
# Digital Human Bridge
# ============================================================

class DigitalHumanBridge:
    """
    Bridge to DigitalSage digital human for pre-consultation.
    """
    
    SYSTEM_PROMPT_CN = """你是KnowHealth的AI医疗助手。你的职责是：
1. 帮助患者准备跨境医疗第二意见的材料
2. 收集患者的病史和症状信息
3. 回答关于服务流程的问题
4. 解释医学术语

请用温暖、专业的语气与患者交流。如果遇到紧急情况，请建议患者立即就医。
你不能提供诊断或治疗建议，只能帮助收集信息和解释流程。"""

    SYSTEM_PROMPT_EN = """You are KnowHealth's AI medical assistant. Your role is to:
1. Help patients prepare materials for cross-border medical second opinions
2. Collect patient medical history and symptom information
3. Answer questions about service processes
4. Explain medical terminology

Please communicate in a warm and professional tone. For emergencies, advise patients to seek immediate medical attention.
You cannot provide diagnoses or treatment recommendations, only help collect information and explain processes."""

    def __init__(self, language: str = "zh"):
        self.language = language
        self.system_prompt = self.SYSTEM_PROMPT_CN if language == "zh" else self.SYSTEM_PROMPT_EN
    
    def get_greeting(self) -> str:
        """Get initial greeting message."""
        if self.language == "zh":
            return """您好！我是KnowHealth的AI医疗助手小知 🏥

我可以帮助您：
📋 收集和整理您的病历信息
🌍 匹配最适合的全球顶级专家
❓ 解答关于跨境医疗咨询的流程问题

请问您今天需要什么帮助？您可以直接告诉我您的病情，或者上传您的病历资料。"""
        else:
            return """Hello! I'm KnowHealth's AI Medical Assistant 🏥

I can help you with:
📋 Collecting and organizing your medical records
🌍 Matching you with the best global experts
❓ Answering questions about cross-border medical consultation

How can I help you today? You can tell me about your condition or upload your medical records."""
    
    def process_message(self, user_message: str, context: Dict = None) -> str:
        """
        Process user message and generate response.
        In production, this would call GPT-4o with the system prompt.
        """
        # Simplified response logic
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["费用", "价格", "多少钱", "cost", "price"]):
            return self._get_pricing_info()
        elif any(word in message_lower for word in ["流程", "步骤", "process", "step"]):
            return self._get_process_info()
        elif any(word in message_lower for word in ["专家", "医生", "expert", "doctor"]):
            return self._get_expert_info()
        else:
            return self._get_general_response(user_message)
    
    def _get_pricing_info(self) -> str:
        if self.language == "zh":
            return """我们的服务定价如下：

💰 AI病历分析：¥499
   - AI自动翻译和结构化病历
   - 智能专家匹配推荐

💰 标准第二意见：¥4,999
   - 1位顶级专家审阅
   - 详细书面意见报告
   - 1次视频会诊

💰 高级多学科：¥9,999
   - 2-3位专家综合会诊
   - 综合意见报告
   - 2次视频会诊

您想了解哪种服务的更多详情？"""
        else:
            return "Our pricing starts at ¥499 for AI analysis..."
    
    def _get_process_info(self) -> str:
        if self.language == "zh":
            return """获取第二意见只需4步：

1️⃣ 上传病历
   上传您的病历、检查报告、影像资料

2️⃣ AI智能分析
   AI自动翻译、结构化、匹配最合适的专家

3️⃣ 专家审阅
   全球顶级专家详细审阅并提供专业意见

4️⃣ 获取报告
   获得详细的第二意见报告，可选视频会诊

整个过程通常需要3-5个工作日。您现在想开始吗？"""
        else:
            return "Getting a second opinion is easy in 4 steps..."
    
    def _get_expert_info(self) -> str:
        if self.language == "zh":
            return """我们合作的专家来自全球顶级医院：

🇺🇸 美国：梅奥诊所、克利夫兰诊所、MD安德森
🇮🇱 以色列：谢巴医疗中心、哈达萨医院
🇯🇵 日本：国立癌症中心、�的大学医院
🇰🇷 韩国：三星医疗中心、首尔大学医院
🇩🇪 德国：夏里特医院

所有专家都经过严格筛选，具有丰富的临床经验。您有偏好的国家或医院吗？"""
        else:
            return "Our experts come from top hospitals worldwide..."
    
    def _get_general_response(self, message: str) -> str:
        if self.language == "zh":
            return f"""感谢您的信息。为了更好地帮助您，请告诉我：

1. 患者的诊断是什么？
2. 目前接受了哪些治疗？
3. 您希望咨询哪个国家的专家？

您也可以直接上传病历资料，我会帮您整理和匹配专家。"""
        else:
            return "Thank you for sharing. To help you better..."


# ============================================================
# Export
# ============================================================

__all__ = [
    "MedicalNLPEngine",
    "ExpertMatchingEngine",
    "DigitalHumanBridge",
    "StructuredMedicalRecord",
    "MedicalEntity",
    "MedicalEntityType",
]
