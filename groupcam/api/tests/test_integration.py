def test_get_cameras(client):
    resp = client.fetch('/cameras')
    assert resp.code == 200
    assert resp.json == {}
