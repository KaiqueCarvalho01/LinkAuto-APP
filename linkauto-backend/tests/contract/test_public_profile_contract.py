from app.models.booking import Booking
from app.models.review import Review
from app.models.user import DetranStatus, InstructorProfile, LicenseType, StudentProfile, User, UserRole


def _seed_contract_profiles(db_session):
    u_inst = User(
        id="inst-contract-1",
        email="inst_contract@secret.com",
        password_hash="secret_hash_pwd",
        roles=[UserRole.INSTRUTOR.value],
        is_active=True,
    )
    p_inst = InstructorProfile(
        user_id="inst-contract-1",
        full_name="Roberto Santos",
        phone="11999990000",
        city="Mogi Mirim",
        state="SP",
        bio="Instrutor credenciado especialista em rodovias.",
        specialties=["Rodovias", "Baliza"],
        price_per_hour=100.0,
        detran_status=DetranStatus.APROVADO.value,
        is_active=True,
        rating_avg=5.0,
        rating_count=1,
    )

    u_pending = User(
        id="inst-contract-pending",
        email="pending@secret.com",
        password_hash="secret_hash_pwd",
        roles=[UserRole.INSTRUTOR.value],
        is_active=True,
    )
    p_pending = InstructorProfile(
        user_id="inst-contract-pending",
        full_name="Instrutor Não Aprovado",
        phone="11988880000",
        city="Mogi Mirim",
        state="SP",
        detran_status=DetranStatus.PENDENTE.value,
        is_active=True,
    )

    u_stud = User(
        id="stud-contract-1",
        email="stud_contract@secret.com",
        password_hash="secret_hash_pwd",
        roles=[UserRole.ALUNO.value],
        is_active=True,
    )
    p_stud = StudentProfile(
        user_id="stud-contract-1",
        full_name="Juliana Costa",
        phone="11977770000",
        city="Mogi Mirim",
        state="SP",
        license_type=LicenseType.EM_PROCESSO.value,
        avatar_url="https://example.com/juliana.jpg",
    )

    b1 = Booking(
        id="b-contract-1",
        student_id="stud-contract-1",
        instructor_id="inst-contract-1",
        status="REALIZADA",
    )

    r1 = Review(
        id="rev-contract-1",
        booking_id="b-contract-1",
        reviewer_id="stud-contract-1",
        reviewed_id="inst-contract-1",
        rating=5,
        comment="Ótima didática!",
    )

    db_session.add_all([u_inst, p_inst, u_pending, p_pending, u_stud, p_stud, b1, r1])
    db_session.commit()


class TestPublicProfileContract:
    def test_get_public_instructor_profile_contract_and_lgpd_sanitization(self, client, db_session):
        _seed_contract_profiles(db_session)

        # Anonymous public request (no Authorization header)
        resp = client.get("/api/v1/instructors/inst-contract-1/public")
        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        data = body["data"]

        # Expected public fields
        assert data["id"] == "inst-contract-1"
        assert data["full_name"] == "Roberto Santos"
        assert data["city"] == "Mogi Mirim"
        assert data["state"] == "SP"
        assert data["bio"] == "Instrutor credenciado especialista em rodovias."
        assert data["specialties"] == ["Rodovias", "Baliza"]
        assert data["price_per_hour"] == 100.0
        assert data["detran_approved"] is True
        assert len(data["reviews"]) == 1
        assert data["reviews"][0]["rating"] == 5
        assert data["reviews"][0]["comment"] == "Ótima didática!"
        assert data["reviews"][0]["reviewer"]["full_name"] == "Juliana Costa"

        # LGPD PII Leakage Protection Check
        data_str = str(data).lower()
        assert "secret" not in data_str
        assert "password" not in data_str
        assert "phone" not in data
        assert "email" not in data
        assert "cpf" not in data
        assert "cnh" not in data
        assert "11999990000" not in data_str

    def test_get_public_instructor_profile_returns_404_for_unapproved_or_missing(self, client, db_session):
        _seed_contract_profiles(db_session)

        # Pending instructor
        resp = client.get("/api/v1/instructors/inst-contract-pending/public")
        assert resp.status_code == 404

        # Non-existent instructor
        resp = client.get("/api/v1/instructors/invalid-id/public")
        assert resp.status_code == 404

    def test_get_public_student_profile_contract_and_lgpd_sanitization(self, client, db_session):
        _seed_contract_profiles(db_session)

        # Anonymous public request (no Authorization header)
        resp = client.get("/api/v1/students/stud-contract-1/public")
        assert resp.status_code == 200
        body = resp.json()
        assert body["error"] is None
        data = body["data"]

        # Expected public fields
        assert data["id"] == "stud-contract-1"
        assert data["full_name"] == "Juliana Costa"
        assert data["city"] == "Mogi Mirim"
        assert data["state"] == "SP"
        assert data["license_type"] == LicenseType.EM_PROCESSO.value
        assert data["completed_lessons_count"] == 1
        assert "rating_avg" in data
        assert "rating_count" in data
        assert "reviews" in data

        # LGPD PII Leakage Protection Check
        data_str = str(data).lower()
        assert "secret" not in data_str
        assert "password" not in data_str
        assert "phone" not in data
        assert "email" not in data
        assert "cpf" not in data
        assert "11977770000" not in data_str

    def test_get_public_student_profile_returns_404_for_missing(self, client, db_session):
        _seed_contract_profiles(db_session)

        resp = client.get("/api/v1/students/invalid-student-id/public")
        assert resp.status_code == 404
