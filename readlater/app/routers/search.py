from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.bookmark import BookmarkListOut
from app.crud import bookmark as bookmark_crud

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=BookmarkListOut)
async def search(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    total, items = await bookmark_crud.list_bookmarks(db, q=q, limit=limit, offset=offset, is_archived=None)
    return {"total": total, "items": items}
