from datetime import datetime
from typing import List

from app.common.domain.models import Id
from ddd import Entity, Attr


class AuthorId(Id):
    pass


class Author(Entity):
    id: AuthorId = Attr()
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
    tags: List = Attr(default=list)
    shown: bool = Attr(default=False)
    created_at: datetime = Attr()
    updated_at: datetime = Attr()
    deleted_at: datetime = Attr()
