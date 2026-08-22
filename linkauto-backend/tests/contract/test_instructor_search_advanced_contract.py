from app.models.user import DetranStatus, InstructorProfile, User, UserRole


def _seed_contract_instructors(db_session):
    instructors_data = [
        ("c-inst-1", "Carlos Baliza", -22.4319, -46.9578, ["Baliza", "Direção Defensiva"], 80.0, 4.9, 25),
        ("c-inst-2", "Ana Rodovia", -22.4400, -46.9600, ["Rodovias", "Baliza"], 110.0, 5.0, 40),
        ("c-inst-3", "Marcos Geral", -22.4200, -46.9400, ["Primeira Habilitação"], 70.0, 4.2, 10),
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
    db_session.commit()


class TestInstructorSearchAdvancedContract:
    def test_search_with_specialty_and_sort(self, client, db_session):
        _seed_contract_instructors(db_session)

        resp = client.get(
            "/api/v1/instructors/search?latitude=-22.4319&longitude=-46.9578&radius_km=30&specialties=Baliza&sort_by=price_desc"
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) == 2
        # price_desc: Ana (110.0) first, Carlos (80.0) second
        assert data[0]["full_name"] == "Ana Rodovia"
        assert data[1]["full_name"] == "Carlos Baliza"

        # Verify zero UUID leakage in public search response
        assert "user_id" not in data[0]
        assert "id" in data[0]
        assert "slug" in data[0]
        assert "c-inst-1" not in str(data)
        assert "c-inst-2" not in str(data)

    def test_search_with_multiple_specialties(self, client, db_session):
        _seed_contract_instructors(db_session)

        resp = client.get(
            "/api/v1/instructors/search?latitude=-22.4319&longitude=-46.9578&radius_km=30&specialties=Rodovias&specialties=Baliza"
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) >= 1
        assert "user_id" not in data[0]
