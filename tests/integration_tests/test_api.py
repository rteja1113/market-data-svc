def test_dam_price_data_api(monkeypatch, Session, client):
    monkeypatch.setattr("src.database.Session", Session)
