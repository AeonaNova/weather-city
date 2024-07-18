import httpx

def test_read_main():
    response = httpx.get("http://localhost:8000/")
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']

def test_search_stats():
    response = httpx.get("http://localhost:8000/api/search-stats")
    assert response.status_code == 200
    print(response.status_code)
    assert 'text/html' in response.headers['content-type']
