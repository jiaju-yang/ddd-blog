from datetime import datetime
from typing import List

from app.common.domain.models import Id
from ddd import Entity, Attr, ValueObject


class Author(ValueObject):
    id: int = Attr()
    name: str = Attr()


class TagId(Id):
    pass


class Tag(Entity):
    id: TagId = Attr()
    name: str = Attr()


class ArticleId(Id):
    pass


class Article(Entity):
    id: ArticleId = Attr()
    title: str = Attr()
    content: str = Attr()
    author: Author = Attr()
    created_at: datetime = Attr()
    updated_at: datetime = Attr(allow_none=True)
    deleted_at: datetime = Attr(allow_none=True)
    tags: List = Attr(default=list)
