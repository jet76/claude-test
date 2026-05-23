from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from datetime import datetime
from app.models.bookmark import Bookmark
from app.models.tag import Tag
from app.models.associations import bookmark_tags
from app.crud.tag import get_or_create_tag


async def create_bookmark(db: AsyncSession, url: str) -> Bookmark | None:
    existing = await db.execute(select(Bookmark).where(Bookmark.url == url))
    if existing.scalar_one_or_none():
        return None
    bookmark = Bookmark(url=url)
    db.add(bookmark)
    await db.commit()
    result = await db.execute(
        select(Bookmark).options(selectinload(Bookmark.tags)).where(Bookmark.id == bookmark.id)
    )
    return result.scalar_one()


async def update_bookmark_metadata(db: AsyncSession, bookmark_id: int, metadata: dict) -> None:
    result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        return
    for key, value in metadata.items():
        if value is not None:
            setattr(bookmark, key, value)
    bookmark.search_text = " ".join(filter(None, [bookmark.title, bookmark.description]))
    bookmark.updated_at = datetime.utcnow()
    await db.commit()


async def get_bookmark(db: AsyncSession, bookmark_id: int) -> Bookmark | None:
    result = await db.execute(
        select(Bookmark).options(selectinload(Bookmark.tags)).where(Bookmark.id == bookmark_id)
    )
    return result.scalar_one_or_none()


async def list_bookmarks(
    db: AsyncSession,
    q: str | None = None,
    tags: list[str] | None = None,
    is_read: bool | None = None,
    is_archived: bool | None = None,
    sort: str = "created_at",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
) -> tuple[int, list[Bookmark]]:
    conditions = []

    if is_read is not None:
        conditions.append(Bookmark.is_read == is_read)
    if is_archived is not None:
        conditions.append(Bookmark.is_archived == is_archived)
    if tags:
        for slug in tags:
            conditions.append(
                Bookmark.id.in_(
                    select(bookmark_tags.c.bookmark_id)
                    .join(Tag, Tag.id == bookmark_tags.c.tag_id)
                    .where(Tag.slug == slug)
                )
            )
    if q:
        pattern = f"%{q}%"
        conditions.append(
            or_(
                Bookmark.title.ilike(pattern),
                Bookmark.description.ilike(pattern),
                Bookmark.url.ilike(pattern),
            )
        )

    sort_col = getattr(Bookmark, sort if sort in ("created_at", "updated_at") else "created_at")
    order_clause = sort_col.asc() if order == "asc" else sort_col.desc()

    base = select(Bookmark).where(*conditions)
    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar_one()

    result = await db.execute(
        select(Bookmark)
        .options(selectinload(Bookmark.tags))
        .where(*conditions)
        .order_by(order_clause)
        .offset(offset)
        .limit(limit)
    )
    return total, list(result.scalars().all())


async def patch_bookmark(db: AsyncSession, bookmark_id: int, data: dict) -> Bookmark | None:
    result = await db.execute(
        select(Bookmark).options(selectinload(Bookmark.tags)).where(Bookmark.id == bookmark_id)
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        return None

    for field in ("title", "description", "is_read", "is_archived"):
        if field in data and data[field] is not None:
            setattr(bookmark, field, data[field])

    if "tags" in data and data["tags"] is not None:
        new_tags = []
        for slug in data["tags"]:
            tag_result = await db.execute(select(Tag).where(Tag.slug == slug))
            tag = tag_result.scalar_one_or_none()
            if not tag:
                tag = await get_or_create_tag(db, slug)
            new_tags.append(tag)
        bookmark.tags = new_tags

    bookmark.search_text = " ".join(filter(None, [bookmark.title, bookmark.description]))
    bookmark.updated_at = datetime.utcnow()
    await db.commit()
    result = await db.execute(
        select(Bookmark).options(selectinload(Bookmark.tags)).where(Bookmark.id == bookmark_id)
    )
    return result.scalar_one()


async def delete_bookmark(db: AsyncSession, bookmark_id: int) -> bool:
    result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        return False
    await db.delete(bookmark)
    await db.commit()
    return True


async def get_graph_data(db: AsyncSession, is_archived: bool = False, limit: int = 500) -> dict:
    from app.config import settings
    result = await db.execute(
        select(Bookmark)
        .options(selectinload(Bookmark.tags))
        .where(Bookmark.is_archived == is_archived)
        .limit(limit)
    )
    bookmarks = list(result.scalars().all())

    nodes = [
        {
            "id": b.id,
            "title": b.title,
            "url": b.url,
            "favicon_url": b.favicon_url,
            "is_read": b.is_read,
            "tags": [t.slug for t in (b.tags or [])],
        }
        for b in bookmarks
    ]

    tag_to_ids: dict[str, list[int]] = {}
    for node in nodes:
        for slug in node["tags"]:
            tag_to_ids.setdefault(slug, []).append(node["id"])

    edge_map: dict[tuple[int, int], list[str]] = {}
    for slug, ids in tag_to_ids.items():
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                key = (min(ids[i], ids[j]), max(ids[i], ids[j]))
                edge_map.setdefault(key, []).append(slug)

    edges = [{"source": src, "target": tgt, "shared_tags": slugs} for (src, tgt), slugs in edge_map.items()]
    return {"nodes": nodes, "edges": edges}
