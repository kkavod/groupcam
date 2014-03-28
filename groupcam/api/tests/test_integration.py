def test_get_cameras(client, db):
    resp = client.fetch('/cameras')
    db.collection.insert({'key': 2})
    res = [stuff for stuff in db.collection.find()]
    import pdb; pdb.set_trace()

    assert resp.code == 200
    assert resp.json == {}
