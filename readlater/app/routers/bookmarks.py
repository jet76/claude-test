from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.bookmark import BookmarkCreate, BookmarkPatch, BookmarkOut, BookmarkListOut, GraphOut
from app.crud import bookmark as bookmark_crud
from app.services.scraper import fetch_metadata
from app.auth import require_api_key

router = APIRouter(prefix="/api/bookmarks", tags=["bookmarks"], dependencies=[Depends(require_api_key)])


async def _scrape_and_update(bookmark_id: int, url: str):
    from app.database import AsyncSessionLocal
    async with AsyncSessionLocal() as db:
        metadata = await fetch_metadata(url)
        await bookmark_crud.update_bookmark_metadata(db, bookmark_id, metadata)


@router.post("", response_model=BookmarkOut, status_code=201)
async def create_bookmark(
    body: BookmarkCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    bookmark = await bookmark_crud.create_bookmark(db, body.url)
    if bookmark is None:
        raise HTTPException(409, "URL already bookmarked")
    background_tasks.add_task(_scrape_and_update, bookmark.id, body.url)
    return bookmark


@router.get("", response_model=BookmarkListOut)
async def list_bookmarks(
    q: str | None = None,
    tags: str | None = None,
    is_read: bool | None = None,
    is_archived: bool | None = Query(default=False),
    sort: str = "created_at",
    order: str = "desc",
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    total, items = await bookmark_crud.list_bookmarks(
        db, q=q, tags=tag_list, is_read=is_read, is_archived=is_archived,
        sort=sort, order=order, limit=limit, offset=offset,
    )
    return {"total": total, "items": items}


@router.get("/graph", response_model=GraphOut)
async def get_graph(
    is_archived: bool = False,
    db: AsyncSession = Depends(get_db),
):
    from app.config import settings
    return await bookmark_crud.get_graph_data(db, is_archived=is_archived, limit=settings.max_graph_nodes)


@router.get("/{bookmark_id}", response_model=BookmarkOut)
async def get_bookmark(bookmark_id: int, db: AsyncSession = Depends(get_db)):
    bookmark = await bookmark_crud.get_bookmark(db, bookmark_id)
    if not bookmark:
        raise HTTPException(404, "Bookmark not found")
    return bookmark


@router.patch("/{bookmark_id}", response_model=BookmarkOut)
async def patch_bookmark(
    bookmark_id: int,
    body: BookmarkPatch,
    db: AsyncSession = Depends(get_db),
):
    bookmark = await bookmark_crud.patch_bookmark(db, bookmark_id, body.model_dump(exclude_unset=True))
    if not bookmark:
        raise HTTPException(404, "Bookmark not found")
    return bookmark


@router.delete("/{bookmark_id}", status_code=204)
async def delete_bookmark(bookmark_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await bookmark_crud.delete_bookmark(db, bookmark_id)
    if not deleted:
        raise HTTPException(404, "Bookmark not found")
