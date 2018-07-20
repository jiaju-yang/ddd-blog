from abc import abstractmethod
from typing import List

from ddd import Repo
from .models import Tag, Article


class TagRepo(Repo):
    __registry_name__ = 'tag'

    @abstractmethod
    def save(self, tag: Tag):
        pass

    @abstractmethod
    def all(self) -> List[Tag]:
        pass


class ArticleRepo(Repo):
    __registry_name__ = 'article'

    @abstractmethod
    def save(self, article: Article):
        pass

    @abstractmethod
    def recently_articles_of_page(self, page=0, page_count=10) -> List[Article]:
        pass
