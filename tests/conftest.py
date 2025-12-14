import pytest
from fellowship import app as flask_app

@pytest.fixture
def app(): 
    """Flask app for testing"""
    flask_app.config["TESTING"] = True
    return flask_app

@pytest.fixture
def client(app):
    """Flask test client"""
    with app.test_client() as client: 
        yield client