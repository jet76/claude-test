from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime
from app.schemas.tag import TagOut


class BookmarkCreate(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class BookmarkPatch(BaseModel):
    title: str | None = None
    description: str | None = None
    is_read: bool | None = None
    is_archived: bool | None = None
    tags: list[str] | None = None  # list of tag slugs


class BookmarkOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    url: str
    title: str | None
    description: str | None
    favicon_url: str | None
    is_read: bool
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    tags: list[TagOut] = []


class BookmarkListOut(BaseModel):
    total: int
    items: list[BookmarkOut]


class GraphNode(BaseModel):
    id: int
    title: str | None
    url: str
    favicon_url: str | None
    is_read: bool
    tags: list[str]  # slugs


class GraphEdge(BaseModel):
    source: int
    target: int
    shared_tags: list[str]


class GraphOut(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
