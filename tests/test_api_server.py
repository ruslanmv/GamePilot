from fastapi.testclient import TestClient

from gamepilot.app.api.server import app


client = TestClient(app)


def test_api_state_and_safety():
    assert client.get('/health').status_code == 200
    assert client.get('/state').status_code == 200
    assert client.get('/safety').status_code == 200


def test_api_command_and_demo():
    r = client.post('/command', json={'text': 'loot'})
    assert r.status_code == 200
    d = client.post('/demo/predict', json={'hp': 20, 'enemy_near': False, 'loot_visible': False})
    assert d.status_code == 200
    assert d.json()['goal'] == 'heal'
