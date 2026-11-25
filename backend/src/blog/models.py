from pydantic import BaseModel

class Post(BaseModel):
    id: int
    author: str = "anonymous"
    title: str
    content: str
    tag: list[str]
    data_posted: str
