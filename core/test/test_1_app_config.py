from settings import ENV


def test_db_config():
    assert ENV == "testing"