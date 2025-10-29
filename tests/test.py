import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_homepage_status(client):
    """Check if the homepage loads successfully"""
    response = client.get('/')
    assert response.status_code == 200

def test_html_contains_metals(client):
    """Ensure the page contains metal names"""
    response = client.get('/')
    html = response.data.decode('utf-8')
    for metal in ['Gold', 'Silver', 'Platinum', 'Copper', 'Iron']:
        assert metal.lower() in html.lower()

