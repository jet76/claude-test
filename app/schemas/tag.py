from pydantic import BaseModel


class TagOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    slug: str
    bookmark_count: int = 0


class TagCreate(BaseModel):
    name: str
