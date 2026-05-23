import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.scraper import fetch_metadata


@pytest.mark.asyncio
async def test_fetch_metadata_success():
    html = """<html><head>
        <meta property="og:title" content="Test Title" />
        <meta property="og:description" content="Test description" />
        <link rel="icon" href="/favicon.ico" />
    </head><body></body></html>"""

    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("app.services.scraper.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_metadata("https://example.com")

    assert result["title"] == "Test Title"
    assert result["description"] == "Test description"
    assert "favicon" in result["favicon_url"]


@pytest.mark.asyncio
async def test_fetch_metadata_fallback_title():
    html = "<html><head><title>Plain Title</title></head><body></body></html>"

    mock_response = MagicMock()
    mock_response.text = html
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)

    with patch("app.services.scraper.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_metadata("https://example.com")

    assert result["title"] == "Plain Title"


@pytest.mark.asyncio
async def test_fetch_metadata_network_error():
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=Exception("Network error"))

    with patch("app.services.scraper.httpx.AsyncClient", return_value=mock_client):
        result = await fetch_metadata("https://example.com")

    assert result == {"title": None, "description": None, "favicon_url": None}
