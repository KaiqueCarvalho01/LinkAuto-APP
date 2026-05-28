from app.models.user import (
    DetranStatus, InstructorProfile, User, UserRole,
)
from app.services.instructor_search_service import InstructorSearchService


def _seed_instructors(db_session):
    for i, (lat, lon, status) in enumerate([
        (-22.43, -46.95, DetranStatus.APROVADO),   # Mogi Mirim
        (-22.44, -46.96, DetranStatus.APROVADO),   # Nearby
        (-23.55, -46.63, DetranStatus.APROVADO),   # São Paulo (far)
        (-22.43, -46.95, DetranStatus.PENDENTE),   # Pending (invisible)
    ]):
        uid = f"search-inst-{i}"
        user = User(id=uid, email=f"si{i}@t.com", password_hash="h", roles=[UserRole.INSTRUTOR.value])
        profile = InstructorProfile(
            user_id=uid, full_name=f"Instructor {i}", phone="1", city="C", state="SP",
            detran_status=status, latitude=lat, longitude=lon, action_radius_km=15, is_active=True,
        )
        db_session.add_all([user, profile])
    db_session.flush()


class TestInstructorSearch:
    def test_returns_only_approved_instructors(self, db_session):
        _seed_instructors(db_session)
        service = InstructorSearchService(db_session)

        results = service.search(latitude=-22.43, longitude=-46.95, radius_km=50)

        statuses = {r.detran_status for r in results}
        assert DetranStatus.PENDENTE.value not in statuses
        assert len(results) >= 2  # At least the two nearby approved ones

    def test_filters_by_distance(self, db_session):
        _seed_instructors(db_session)
        service = InstructorSearchService(db_session)

        results = service.search(latitude=-22.43, longitude=-46.95, radius_km=5)

        # Only the very close ones (Mogi Mirim area), not São Paulo
        assert len(results) <= 2
