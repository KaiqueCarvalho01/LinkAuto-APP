from fastapi.testclient import TestClient
from app.main import create_app

client = TestClient(create_app())


def test_register_with_admin_role_is_blocked():
    """
    D01 - P0: Bloquear ADMIN no registro público
    Tenta registrar uma conta enviando a role 'ADMIN'. Deve retornar 400 Bad Request.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "malicious-admin@example.com",
            "password": "attack-password-123",
            "roles": ["ADMIN"]
        }
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["error"] is not None
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert "FORBIDDEN_ROLE" in payload["error"]["message"]


def _register_and_login_user(email: str, roles: list[str]) -> tuple[str, str]:
    from app.services.us1_store import get_identity_store
    from app.core.security import hash_password
    
    try:
        user = get_identity_store().create_user(
            email=email,
            password_hash=hash_password("strong-password"),
            roles=roles
        )
        user_id = user.id
    except ValueError:
        user_id = get_identity_store().get_user_by_email(email).id

    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "strong-password"}
    )
    return login_resp.json()["data"]["access_token"], user_id


def test_patch_profile_rejects_extra_and_system_fields():
    """
    D03 - P1: Fechar schema de profile update (mass assignment)
    Tentativas de atualizar campos restritos como detran_status, rating_avg, rating_count,
    ou campos não declarados (is_admin) devem retornar erro de validação.
    """
    token, _ = _register_and_login_user("test-instructor-abuse@example.com", ["ALUNO", "INSTRUTOR"])
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Tenta alterar detran_status
    response = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={
            "instructor_profile": {
                "detran_status": "APROVADO"
            }
        }
    )
    # Deve ser rejeitado (422 Unprocessable Entity ou 400 Bad Request)
    assert response.status_code in (400, 422)

    # 2. Tenta alterar rating_avg
    response = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={
            "instructor_profile": {
                "rating_avg": 5.0
            }
        }
    )
    assert response.status_code in (400, 422)

    # 3. Tenta passar campo inexistente is_admin no nível do root
    response = client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={
            "is_admin": True
        }
    )
    assert response.status_code in (400, 422)


def test_security_headers_are_present():
    """
    D04 - P1: Security headers middleware
    Verifica se os cabeçalhos de segurança essenciais estão presentes nas respostas HTTP.
    """
    response = client.get("/api/v1/foundation/ping")
    assert response.status_code == 200
    
    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "camera=()" in headers.get("Permissions-Policy", "")
    assert "no-store" in headers.get("Cache-Control", "")


def test_upload_with_fake_mime_is_rejected():
    """
    D06 - P1: Elevar validação de upload (magic bytes)
    Tenta realizar upload de um arquivo com MIME 'application/pdf' contendo dados
    comuns que não começam com a assinatura PDF (%PDF). Deve retornar 400 Bad Request.
    """
    token, user_id = _register_and_login_user("test-uploader@example.com", ["INSTRUTOR"])
    headers = {"Authorization": f"Bearer {token}"}
    
    # Detran credential com MIME correto mas magic bytes falsos (texto comum)
    response = client.post(
        f"/api/v1/instructors/{user_id}/documents",
        headers=headers,
        files={
            "detran_credential": ("credential.pdf", b"fake-pdf-content", "application/pdf"),
            "criminal_record": ("record.pdf", b"%PDF-1.4\nsample", "application/pdf"),
        },
    )
    
    assert response.status_code == 400
    payload = response.json()
    assert payload["error"] is not None
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert "INVALID_FILE_CONTENT" in payload["error"]["message"]


def test_rate_limit_on_login():
    """
    D09 - P2: Rate limiting com slowapi
    Simula uma rajada de requisições no endpoint de login.
    A partir da 11ª requisição no mesmo minuto, o servidor deve responder com 429 Too Many Requests.
    """
    # Como o rate limiter é baseado em memória por IP, o TestClient padrão simula do mesmo IP
    # Vamos enviar 10 requisições seguidas (limite do threshold)
    for _ in range(10):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "rate-limit-test@example.com", "password": "wrong-password"}
        )
        # Podem falhar com 401 Unauthorized por causa das credenciais incorretas
        assert response.status_code == 401

    # A 11ª requisição deve estourar o limite e retornar 429
    excess_response = client.post(
        "/api/v1/auth/login",
        json={"email": "rate-limit-test@example.com", "password": "wrong-password"}
    )
    assert excess_response.status_code == 429
    payload = excess_response.json()
    assert payload["error"] is not None
    assert payload["error"]["code"] == "RATE_LIMIT_EXCEEDED"




