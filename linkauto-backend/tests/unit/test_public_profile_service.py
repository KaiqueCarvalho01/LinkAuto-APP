import pytest
from app.models.booking import Booking
from app.models.review import Review
from app.models.user import DetranStatus, InstructorProfile, LicenseType, StudentProfile, User, UserRole
from app.services.public_profile_service import PublicProfileService


def _seed_public_profiles_data(db_session):
    # 1. Approved Instructor
    u_inst = User(
        id="inst-pub-1",
        email="inst1@secret.com",
        password_hash="secret_hash",
        roles=[UserRole.INSTRUTOR.value],
        is_active=True,
    )
    p_inst = InstructorProfile(
        user_id="inst-pub-1",
        full_name="Carlos Silva Instrutor",
        phone="11999998888",
        city="Mogi Mirim",
        state="SP",
        bio="Instrutor experiente com mais de 10 anos de atuação.",
        specialties=["Baliza", "Rodovias"],
        price_per_hour=95.0,
        detran_status=DetranStatus.APROVADO.value,
        is_active=True,
        rating_avg=4.8,
        rating_count=5,
    )

    # 2. Pending Instructor (should return 404)
    u_inst_pending = User(
        id="inst-pub-pending",
        email="pending@secret.com",
        password_hash="secret_hash",
        roles=[UserRole.INSTRUTOR.value],
        is_active=True,
    )
    p_inst_pending = InstructorProfile(
        user_id="inst-pub-pending",
        full_name="Instrutor Pendente",
        phone="11999997777",
        city="Mogi Mirim",
        state="SP",
        detran_status=DetranStatus.PENDENTE.value,
        is_active=True,
    )

    # 3. Student 1 (Reviewer & Target)
    u_stud1 = User(
        id="stud-pub-1",
        email="stud1@secret.com",
        password_hash="secret_hash",
        roles=[UserRole.ALUNO.value],
        is_active=True,
    )
    p_stud1 = StudentProfile(
        user_id="stud-pub-1",
        full_name="Ana Paula Aluna",
        phone="11988887777",
        city="Mogi Mirim",
        state="SP",
        license_type=LicenseType.EM_PROCESSO.value,
        avatar_url="https://example.com/ana.jpg",
    )

    # 4. Student 2
    u_stud2 = User(
        id="stud-pub-2",
        email="stud2@secret.com",
        password_hash="secret_hash",
        roles=[UserRole.ALUNO.value],
        is_active=True,
    )
    p_stud2 = StudentProfile(
        user_id="stud-pub-2",
        full_name="Bruno Aluno",
        phone="11977776666",
        city="Mogi Mirim",
        state="SP",
        license_type=LicenseType.B.value,
    )

    # 5. Bookings
    b1 = Booking(
        id="b-pub-1",
        student_id="stud-pub-1",
        instructor_id="inst-pub-1",
        status="REALIZADA",
    )
    b2 = Booking(
        id="b-pub-2",
        student_id="stud-pub-1",
        instructor_id="inst-pub-1",
        status="REALIZADA",
    )

    # 6. Reviews: Student 1 reviewed Instructor 1, Instructor 1 reviewed Student 1
    r_inst = Review(
        id="rev-inst-1",
        booking_id="b-pub-1",
        reviewer_id="stud-pub-1",
        reviewed_id="inst-pub-1",
        rating=5,
        comment="Excelente aula de baliza!",
    )
    r_stud = Review(
        id="rev-stud-1",
        booking_id="b-pub-1",
        reviewer_id="inst-pub-1",
        reviewed_id="stud-pub-1",
        rating=5,
        comment="Aluna muito dedicada e pontual.",
    )

    db_session.add_all([
        u_inst, p_inst,
        u_inst_pending, p_inst_pending,
        u_stud1, p_stud1,
        u_stud2, p_stud2,
        b1, b2,
        r_inst, r_stud,
    ])
    db_session.flush()


class TestPublicProfileService:
    def test_get_public_instructor_profile_success(self, db_session):
        _seed_public_profiles_data(db_session)
        service = PublicProfileService(db_session)

        profile = service.get_public_instructor("inst-pub-1")

        assert profile.id == "inst-pub-1"
        assert profile.full_name == "Carlos Silva Instrutor"
        assert profile.city == "Mogi Mirim"
        assert profile.state == "SP"
        assert profile.bio == "Instrutor experiente com mais de 10 anos de atuação."
        assert profile.specialties == ["Baliza", "Rodovias"]
        assert profile.price_per_hour == 95.0
        assert profile.detran_approved is True
        assert len(profile.reviews) == 1
        assert profile.reviews[0].rating == 5
        assert profile.reviews[0].comment == "Excelente aula de baliza!"
        assert profile.reviews[0].reviewer.full_name == "Ana Paula Aluna"
        assert profile.reviews[0].reviewer.avatar_url == "https://example.com/ana.jpg"

    def test_get_public_instructor_pending_or_inactive_raises_value_error(self, db_session):
        _seed_public_profiles_data(db_session)
        service = PublicProfileService(db_session)

        # Pending instructor must raise ValueError (treated as 404 in endpoint)
        with pytest.raises(ValueError, match="Instructor not found or not approved"):
            service.get_public_instructor("inst-pub-pending")

        # Non-existent instructor
        with pytest.raises(ValueError, match="Instructor not found or not approved"):
            service.get_public_instructor("non-existent-id")

    def test_get_public_student_profile_success(self, db_session):
        _seed_public_profiles_data(db_session)
        service = PublicProfileService(db_session)

        profile = service.get_public_student("stud-pub-1")

        assert profile.id == "stud-pub-1"
        assert profile.full_name == "Ana Paula Aluna"
        assert profile.city == "Mogi Mirim"
        assert profile.state == "SP"
        assert profile.license_type == LicenseType.EM_PROCESSO.value
        assert profile.completed_lessons_count == 2
        assert profile.rating_avg == 5.0
        assert profile.rating_count == 1
        assert len(profile.reviews) == 1
        assert profile.reviews[0].rating == 5
        assert profile.reviews[0].comment == "Aluna muito dedicada e pontual."
        assert profile.reviews[0].reviewer.full_name == "Carlos Silva Instrutor"

    def test_get_public_student_non_existent_raises_value_error(self, db_session):
        _seed_public_profiles_data(db_session)
        service = PublicProfileService(db_session)

        with pytest.raises(ValueError, match="Student not found"):
            service.get_public_student("non-existent-id")
