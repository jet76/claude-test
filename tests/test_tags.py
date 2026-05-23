import pytest


@pytest.mark.asyncio
async def test_list_tags_empty(client):
    res = await client.get("/api/tags")
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_create_tag(client):
    res = await client.post("/api/tags", json={"name": "Python"})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Python"
    assert data["slug"] == "python"


@pytest.mark.asyncio
async def test_create_tag_duplicate(client):
    await client.post("/api/tags", json={"name": "Python"})
    res = await client.post("/api/tags", json={"name": "Python"})
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_delete_tag(client):
    create = await client.post("/api/tags", json={"name": "ToDelete"})
    tag_id = create.json()["id"]
    res = await client.delete(f"/api/tags/{tag_id}")
    assert res.status_code == 204


@pytest.mark.asyncio
async def test_delete_tag_not_found(client):
    res = await client.delete("/api/tags/9999")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_tag_bookmark_count(client):
    create = await client.post("/api/bookmarks", json={"url": "https://example.com"})
    bm_id = create.json()["id"]
    await client.patch(f"/api/bookmarks/{bm_id}", json={"tags": ["python"]})

    res = await client.get("/api/tags")
    assert res.status_code == 200
    tags = res.json()
    python_tag = next((t for t in tags if t["slug"] == "python"), None)
    assert python_tag is not None
    assert python_tag["bookmark_count"] == 1
