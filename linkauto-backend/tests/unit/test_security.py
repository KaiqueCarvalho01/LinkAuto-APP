from app.core.security import hash_password, verify_password


def test_hash_and_verify_round_trip():
    password_hash = hash_password("password123")
    assert verify_password("password123", password_hash)
    assert not verify_password("wrong-password", password_hash)


def test_passwords_longer_than_72_bytes_are_supported():
    long_password = "a" * 80
    password_hash = hash_password(long_password)
    assert verify_password(long_password, password_hash)
    # bcrypt only considers the first 72 bytes (legacy bcrypt<5 behaviour).
    assert verify_password("a" * 72, password_hash)


def test_multibyte_password_longer_than_72_bytes_is_supported():
    long_password = "ç" * 50  # 100 bytes in UTF-8
    password_hash = hash_password(long_password)
    assert verify_password(long_password, password_hash)
