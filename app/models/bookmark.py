from __future__ import annotations
import sqlalchemy as sa
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from typing import TYPE_CHECKING, List
from app.database import Base
from app.models.associations import bookmark_tags

if TYPE_CHECKING:
    from app.models.tag import Tag


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    url: Mapped[str] = mapped_column(sa.Text, nullable=False, unique=True)
    title: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    favicon_url: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    is_archived: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    search_text: Mapped[str | None] = mapped_column(sa.Text, nullable=True)

    tags: Mapped[List[Tag]] = relationship(
        "Tag", secondary=bookmark_tags, back_populates="bookmarks", lazy="selectin"
    )

    __table_args__ = (
        sa.Index("ix_bookmarks_is_read", "is_read"),
        sa.Index("ix_bookmarks_is_archived", "is_archived"),
        sa.Index("ix_bookmarks_created_at", "created_at"),
    )
