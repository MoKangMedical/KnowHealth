import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """测试根路径接口"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "KnowHealth"
    assert data["version"] == "0.1.0"
    assert data["status"] == "running"
    assert "timestamp" in data


def test_health_check(client: TestClient):
    """测试健康检查接口"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "users" in data
    assert "cases" in data
    assert "experts" in data
    assert "timestamp" in data


def test_user_register(client: TestClient):
    """测试用户注册接口"""
    user_data = {
        "phone": "+8613800138000",
        "name": "测试用户",
        "email": "test@example.com",
        "role": "patient",
        "language": "zh-CN"
    }
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "+8613800138000"
    assert data["name"] == "测试用户"
    assert data["role"] == "patient"
    assert "id" in data
    assert "token" not in data  # response_model=UserResponse doesn't include token


def test_user_register_duplicate_phone(client: TestClient):
    """测试重复手机号注册失败"""
    user_data = {
        "phone": "+8613800138001",
        "name": "第一个用户",
        "role": "patient"
    }
    # Register first time
    client.post("/api/v1/auth/register", json=user_data)
    # Register again with same phone
    user_data["name"] = "第二个用户"
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400


def test_user_login(client: TestClient):
    """测试用户登录接口"""
    # First register a user
    user_data = {
        "phone": "+8613800138002",
        "name": "登录测试用户",
        "role": "patient"
    }
    reg_response = client.post("/api/v1/auth/register", json=user_data)
    assert reg_response.status_code == 200

    # Login with form data (phone field)
    login_response = client.post(
        "/api/v1/auth/login",
        data={"phone": "+8613800138002"}
    )
    assert login_response.status_code == 200
    data = login_response.json()
    assert "token" in data
    assert "user_id" in data
    assert data["name"] == "登录测试用户"
    assert data["role"] == "patient"


def test_user_login_nonexistent(client: TestClient):
    """测试不存在的用户登录失败"""
    response = client.post(
        "/api/v1/auth/login",
        data={"phone": "+8699999999999"}
    )
    assert response.status_code == 404


def test_protected_endpoint_without_token(client: TestClient):
    """测试需要认证的接口（无令牌）"""
    response = client.get("/api/v1/cases")
    assert response.status_code == 401


def test_protected_endpoint_with_invalid_token(client: TestClient):
    """测试需要认证的接口（无效令牌）"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/cases", headers=headers)
    assert response.status_code == 401


def test_list_experts(client: TestClient):
    """测试获取专家列表（无需认证）"""
    response = client.get("/api/v1/experts")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "experts" in data
    assert data["total"] >= 1  # sample experts are pre-loaded


def test_list_experts_with_filters(client: TestClient):
    """测试按条件筛选专家"""
    response = client.get("/api/v1/experts?country=US")
    assert response.status_code == 200
    data = response.json()
    for expert in data["experts"]:
        assert expert["country"] == "US"


def test_get_expert(client: TestClient):
    """测试获取单个专家详情"""
    response = client.get("/api/v1/experts/exp_001")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "exp_001"
    assert data["name"] == "Dr. James Wilson"
    assert data["hospital"] == "Mayo Clinic"


def test_get_expert_not_found(client: TestClient):
    """测试获取不存在的专家"""
    response = client.get("/api/v1/experts/nonexistent")
    assert response.status_code == 404


def test_get_stats(client: TestClient):
    """测试平台统计接口（无需认证）"""
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_cases" in data
    assert "total_experts" in data
    assert "total_orders" in data


def test_create_case_and_full_flow(client: TestClient):
    """测试创建病例及完整流程"""
    # Register a patient
    user_data = {
        "phone": "+8613800138010",
        "name": "流程测试患者",
        "role": "patient"
    }
    reg_response = client.post("/api/v1/auth/register", json=user_data)
    assert reg_response.status_code == 200

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={"phone": "+8613800138010"}
    )
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a case
    case_data = {
        "disease_type": "lung_cancer",
        "description": "患者55岁男性，确诊肺腺癌III期，寻求第二诊疗意见",
        "urgency": "normal",
        "preferred_countries": ["US", "JP"],
        "preferred_languages": ["en", "zh"]
    }
    case_response = client.post("/api/v1/cases", json=case_data, headers=headers)
    assert case_response.status_code == 200
    case = case_response.json()
    case_id = case["id"]
    assert case["disease_type"] == "lung_cancer"
    assert case["status"] == "pending"

    # Get the case
    get_response = client.get(f"/api/v1/cases/{case_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == case_id

    # List cases
    list_response = client.get("/api/v1/cases", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] >= 1

    # AI Summarize
    summary_data = {"case_id": case_id, "language": "en"}
    summary_response = client.post("/api/v1/ai/summarize", json=summary_data, headers=headers)
    assert summary_response.status_code == 200
    assert "summary" in summary_response.json()
    assert "structured_data" in summary_response.json()

    # Match experts
    match_data = {"case_id": case_id, "top_n": 3}
    match_response = client.post("/api/v1/experts/match", json=match_data, headers=headers)
    assert match_response.status_code == 200
    assert "matched_experts" in match_response.json()

    # Get opinion
    opinion_response = client.get(f"/api/v1/opinions/{case_id}", headers=headers)
    assert opinion_response.status_code == 200
    assert "opinion" in opinion_response.json()

    # Create order
    order_data = {"case_id": case_id, "service_tier": "standard"}
    order_response = client.post("/api/v1/orders", json=order_data, headers=headers)
    assert order_response.status_code == 200
    order = order_response.json()
    assert order["payment_status"] == "pending"
    assert order["amount"] == 4999

    # Pay order
    order_id = order["id"]
    pay_response = client.post(f"/api/v1/orders/{order_id}/pay", headers=headers)
    assert pay_response.status_code == 200
    assert pay_response.json()["status"] == "paid"


def test_create_case_without_auth(client: TestClient):
    """测试未认证时创建病例失败"""
    case_data = {
        "disease_type": "lung_cancer",
        "description": "患者55岁男性，确诊肺腺癌III期",
        "urgency": "normal"
    }
    response = client.post("/api/v1/cases", json=case_data)
    assert response.status_code == 401


def test_expert_cannot_create_case(client: TestClient):
    """测试专家角色无法创建病例"""
    # Register an expert
    user_data = {
        "phone": "+8613800138020",
        "name": "测试专家",
        "role": "expert"
    }
    client.post("/api/v1/auth/register", json=user_data)
    login_response = client.post(
        "/api/v1/auth/login",
        data={"phone": "+8613800138020"}
    )
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    case_data = {
        "disease_type": "lung_cancer",
        "description": "专家角色尝试创建病例以验证权限控制",
        "urgency": "normal"
    }
    response = client.post("/api/v1/cases", json=case_data, headers=headers)
    assert response.status_code == 403
