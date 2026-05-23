import sqlalchemy as sa
from app.database import Base

bookmark_tags = sa.Table(
    "bookmark_tags",
    Base.metadata,
    sa.Column("bookmark_id", sa.Integer, sa.ForeignKey("bookmarks.id", ondelete="CASCADE"), primary_key=True),
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
