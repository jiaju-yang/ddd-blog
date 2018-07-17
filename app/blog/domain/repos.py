from abc import abstractmethod, ABC
from typing import List

from .models import Tag, Article


class TagRepo(ABC):
    @abstractmethod
    def save(self, tag: Tag):
        pass

    @abstractmethod
    def all(self) -> List[Tag]:
        pass


class ArticleRepo(ABC):
    @abstractmethod
    def save(self, article: Article):
        pass

    @abstractmethod
    def recently_articles_of_page(self, page=0, page_count=10) -> List[Article]:
        pass
