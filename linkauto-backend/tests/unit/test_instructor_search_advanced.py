from app.models.user import DetranStatus, InstructorProfile, User, UserRole
from app.services.instructor_search_service import InstructorSearchService


def _seed_advanced_instructors(db_session):
    instructors_data = [
        # (id, name, lat, lon, specialties, price, rating_avg, rating_count)
        ("adv-1", "Carlos Baliza", -22.4319, -46.9578, ["Baliza", "Direção Defensiva"], 80.0, 4.9, 25),
        ("adv-2", "Ana Rodovia", -22.4400, -46.9600, ["Rodovias", "Baliza"], 110.0, 5.0, 40),
        ("adv-3", "Marcos Geral", -22.4200, -46.9400, ["Primeira Habilitação"], 70.0, 4.2, 10),
    ]
    for uid, name, lat, lon, specs, price, rating, count in instructors_data:
        user = User(id=uid, email=f"{uid}@test.com", password_hash="hash", roles=[UserRole.INSTRUTOR.value])
        profile = InstructorProfile(
            user_id=uid,
            full_name=name,
            phone="19999999999",
            city="Mogi Mirim",
            state="SP",
            detran_status=DetranStatus.APROVADO.value,
            latitude=lat,
            longitude=lon,
            specialties=specs,
            price_per_hour=price,
            rating_avg=rating,
            rating_count=count,
            action_radius_km=20,
            is_active=True,
        )
        db_session.add_all([user, profile])
    db_session.flush()


class TestInstructorSearchAdvanced:
    def test_filter_by_single_specialty(self, db_session):
        _seed_advanced_instructors(db_session)
        service = InstructorSearchService(db_session)

        results = service.search(
            latitude=-22.4319,
            longitude=-46.9578,
            radius_km=30,
            specialties=["Rodovias"],
        )
        assert len(results) == 1
        assert results[0].full_name == "Ana Rodovia"

    def test_filter_by_specialty_case_insensitive(self, db_session):
        _seed_advanced_instructors(db_session)
        service = InstructorSearchService(db_session)

        results = service.search(
            latitude=-22.4319,
            longitude=-46.9578,
            radius_km=30,
            specialties=["baliza"],
        )
        assert len(results) == 2
        names = {r.full_name for r in results}
        assert names == {"Carlos Baliza", "Ana Rodovia"}

    def test_sort_by_price_asc(self, db_session):
        _seed_advanced_instructors(db_session)
        service = InstructorSearchService(db_session)

        results = service.search(
            latitude=-22.4319,
            longitude=-46.9578,
            radius_km=30,
            sort_by="price_asc",
        )
        prices = [float(r.price_per_hour) for r in results]
        assert prices == [70.0, 80.0, 110.0]

    def test_sort_by_price_desc(self, db_session):
        _seed_advanced_instructors(db_session)
        service = InstructorSearchService(db_session)

        results = service.search(
            latitude=-22.4319,
            longitude=-46.9578,
            radius_km=30,
            sort_by="price_desc",
        )
        prices = [float(r.price_per_hour) for r in results]
        assert prices == [110.0, 80.0, 70.0]

    def test_sort_by_rating(self, db_session):
        _seed_advanced_instructors(db_session)
        service = InstructorSearchService(db_session)

        results = service.search(
            latitude=-22.4319,
            longitude=-46.9578,
            radius_km=30,
            sort_by="rating",
        )
        ratings = [r.rating_avg for r in results]
        assert ratings == [5.0, 4.9, 4.2]

    def test_sort_by_distance(self, db_session):
        _seed_advanced_instructors(db_session)
        service = InstructorSearchService(db_session)

        # Origin is exactly Carlos Baliza's position (-22.4319, -46.9578)
        results = service.search(
            latitude=-22.4319,
            longitude=-46.9578,
            radius_km=30,
            sort_by="distance",
        )
        assert results[0].full_name == "Carlos Baliza"
