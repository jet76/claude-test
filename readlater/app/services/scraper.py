import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.config import settings


async def fetch_metadata(url: str) -> dict:
    result = {"title": None, "description": None, "favicon_url": None}
    try:
        async with httpx.AsyncClient(timeout=settings.scrape_timeout, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "ReadLater/1.0"})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            title_tag = soup.find("meta", property="og:title") or soup.find("title")
            if title_tag:
                result["title"] = (
                    title_tag.get("content") or title_tag.get_text()
                ).strip()[:512]

            desc_tag = (
                soup.find("meta", property="og:description")
                or soup.find("meta", attrs={"name": "description"})
            )
            if desc_tag:
                result["description"] = (desc_tag.get("content") or "").strip()[:1024]

            favicon = soup.find("link", rel=lambda r: r and "icon" in r)
            if favicon and favicon.get("href"):
                result["favicon_url"] = urljoin(url, favicon["href"])
            else:
                parsed = urlparse(url)
                result["favicon_url"] = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"

    except Exception:
        pass

    return result
