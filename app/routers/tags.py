from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.tag import TagOut, TagCreate
from app.crud import tag as tag_crud
from app.auth import require_api_key

router = APIRouter(prefix="/api/tags", tags=["tags"], dependencies=[Depends(require_api_key)])


@router.get("", response_model=list[TagOut])
async def list_tags(db: AsyncSession = Depends(get_db)):
    return await tag_crud.get_all_tags(db)


@router.post("", response_model=TagOut, status_code=201)
async def create_tag(body: TagCreate, db: AsyncSession = Depends(get_db)):
    tag = await tag_crud.create_tag(db, body.name)
    if tag is None:
        raise HTTPException(409, "Tag already exists")
    return {"id": tag.id, "name": tag.name, "slug": tag.slug, "bookmark_count": 0}


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await tag_crud.delete_tag(db, tag_id)
    if not deleted:
        raise HTTPException(404, "Tag not found")
