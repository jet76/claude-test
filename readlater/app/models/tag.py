from __future__ import annotations
import sqlalchemy as sa
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING, List
from app.database import Base
from app.models.associations import bookmark_tags

if TYPE_CHECKING:
    from app.models.bookmark import Bookmark


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(sa.Text, nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(sa.Text, nullable=False, unique=True)

    bookmarks: Mapped[List[Bookmark]] = relationship(
        "Bookmark", secondary=bookmark_tags, back_populates="tags", lazy="selectin"
    )
