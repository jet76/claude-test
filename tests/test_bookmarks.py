import pytest


@pytest.mark.asyncio
async def test_create_bookmark(client):
    res = await client.post("/api/bookmarks", json={"url": "https://example.com"})
    assert res.status_code == 201
    data = res.json()
    assert data["url"] == "https://example.com"
    assert data["is_read"] is False
    assert data["is_archived"] is False


@pytest.mark.asyncio
async def test_create_bookmark_duplicate(client):
    await client.post("/api/bookmarks", json={"url": "https://example.com"})
    res = await client.post("/api/bookmarks", json={"url": "https://example.com"})
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_create_bookmark_invalid_url(client):
    res = await client.post("/api/bookmarks", json={"url": "not-a-url"})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_list_bookmarks_empty(client):
    res = await client.get("/api/bookmarks")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_list_bookmarks(client):
    await client.post("/api/bookmarks", json={"url": "https://example.com"})
    await client.post("/api/bookmarks", json={"url": "https://example.org"})
    res = await client.get("/api/bookmarks")
    assert res.status_code == 200
    assert res.json()["total"] == 2


@pytest.mark.asyncio
async def test_get_bookmark(client):
    create = await client.post("/api/bookmarks", json={"url": "https://example.com"})
    bm_id = create.json()["id"]
    res = await client.get(f"/api/bookmarks/{bm_id}")
    assert res.status_code == 200
    assert res.json()["id"] == bm_id


@pytest.mark.asyncio
async def test_get_bookmark_not_found(client):
    res = await client.get("/api/bookmarks/9999")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_patch_bookmark_mark_read(client):
    create = await client.post("/api/bookmarks", json={"url": "https://example.com"})
    bm_id = create.json()["id"]
    res = await client.patch(f"/api/bookmarks/{bm_id}", json={"is_read": True})
    assert res.status_code == 200
    assert res.json()["is_read"] is True


@pytest.mark.asyncio
async def test_patch_bookmark_archive(client):
    create = await client.post("/api/bookmarks", json={"url": "https://example.com"})
    bm_id = create.json()["id"]
    res = await client.patch(f"/api/bookmarks/{bm_id}", json={"is_archived": True})
    assert res.status_code == 200
    assert res.json()["is_archived"] is True


@pytest.mark.asyncio
async def test_patch_bookmark_tags(client):
    create = await client.post("/api/bookmarks", json={"url": "https://example.com"})
    bm_id = create.json()["id"]
    res = await client.patch(f"/api/bookmarks/{bm_id}", json={"tags": ["python", "web"]})
    assert res.status_code == 200
    tag_slugs = [t["slug"] for t in res.json()["tags"]]
    assert "python" in tag_slugs
    assert "web" in tag_slugs


@pytest.mark.asyncio
async def test_delete_bookmark(client):
    create = await client.post("/api/bookmarks", json={"url": "https://example.com"})
    bm_id = create.json()["id"]
    res = await client.delete(f"/api/bookmarks/{bm_id}")
    assert res.status_code == 204
    res2 = await client.get(f"/api/bookmarks/{bm_id}")
    assert res2.status_code == 404


@pytest.mark.asyncio
async def test_search_bookmarks(client):
    await client.post("/api/bookmarks", json={"url": "https://example.com"})
    res = await client.get("/api/search?q=example")
    assert res.status_code == 200
    assert res.json()["total"] >= 1


@pytest.mark.asyncio
async def test_filter_by_tag(client):
    create = await client.post("/api/bookmarks", json={"url": "https://example.com"})
    bm_id = create.json()["id"]
    await client.patch(f"/api/bookmarks/{bm_id}", json={"tags": ["python"]})
    await client.post("/api/bookmarks", json={"url": "https://other.com"})

    res = await client.get("/api/bookmarks?tags=python")
    assert res.status_code == 200
    assert res.json()["total"] == 1


@pytest.mark.asyncio
async def test_graph_endpoint(client):
    create = await client.post("/api/bookmarks", json={"url": "https://a.com"})
    bm1 = create.json()["id"]
    create2 = await client.post("/api/bookmarks", json={"url": "https://b.com"})
    bm2 = create2.json()["id"]
    await client.patch(f"/api/bookmarks/{bm1}", json={"tags": ["python"]})
    await client.patch(f"/api/bookmarks/{bm2}", json={"tags": ["python"]})

    res = await client.get("/api/bookmarks/graph")
    assert res.status_code == 200
    data = res.json()
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1
    assert "python" in data["edges"][0]["shared_tags"]
