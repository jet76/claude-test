from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from slugify import slugify
from app.models.bookmark import Bookmark
from app.models.tag import Tag
from app.models.associations import bookmark_tags


async def get_all_tags(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(Tag, func.count(bookmark_tags.c.bookmark_id).label("bookmark_count"))
        .outerjoin(bookmark_tags, Tag.id == bookmark_tags.c.tag_id)
        .group_by(Tag.id)
        .order_by(Tag.name)
    )
    rows = result.all()
    tags = []
    for tag, count in rows:
        tags.append({"id": tag.id, "name": tag.name, "slug": tag.slug, "bookmark_count": count})
    return tags


async def get_or_create_tag(db: AsyncSession, name: str) -> Tag:
    slug = slugify(name)
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    tag = result.scalar_one_or_none()
    if not tag:
        tag = Tag(name=name, slug=slug)
        db.add(tag)
        await db.flush()
    return tag


async def create_tag(db: AsyncSession, name: str) -> Tag | None:
    slug = slugify(name)
    existing = await db.execute(select(Tag).where(Tag.slug == slug))
    if existing.scalar_one_or_none():
        return None
    tag = Tag(name=name, slug=slug)
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


async def delete_tag(db: AsyncSession, tag_id: int) -> bool:
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        return False
    await db.delete(tag)
    await db.commit()
    return True
