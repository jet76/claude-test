import ipaddress
import socket
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from app.config import settings

_SAFE_SCHEMES = {"http", "https"}

_PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
]


def _is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in _SAFE_SCHEMES:
        return False
    try:
        ip = ipaddress.ip_address(socket.gethostbyname(parsed.hostname or ""))
        return not any(ip in net for net in _PRIVATE_NETWORKS)
    except Exception:
        return False


def _safe_favicon(url: str, href: str) -> str | None:
    resolved = urljoin(url, href)
    parsed = urlparse(resolved)
    if parsed.scheme not in _SAFE_SCHEMES:
        return None
    return resolved


async def fetch_metadata(url: str) -> dict:
    result = {"title": None, "description": None, "favicon_url": None}

    if not _is_safe_url(url):
        return result

    try:
        async with httpx.AsyncClient(
            timeout=settings.scrape_timeout,
            follow_redirects=True,
        ) as client:
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
                result["favicon_url"] = _safe_favicon(url, favicon["href"])
            else:
                parsed = urlparse(url)
                result["favicon_url"] = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"

    except Exception:
        pass

    return result
