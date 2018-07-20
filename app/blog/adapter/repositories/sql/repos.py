from typing import List

from app.blog.domain.models import Tag, Article
from app.blog.domain.repos import TagRepo, ArticleRepo
from app.common.adapter.repositories.sql import db


class SqlTagRepo(TagRepo):
    def save(self, tag: Tag):
        db.session.merge(tag)
        db.session.commit()

    def all(self) -> List[Tag]:
        return db.session.query(Tag).all()


class SqlArticleRepo(ArticleRepo):
    def save(self, article: Article):
        db.session.merge(article)
        db.session.commit()

    def recently_articles_of_page(self, page=0, page_count=10) -> List[Article]:
        return db.session.query(Article).order_by(Article.created_at)[
               page * page_count: (page + 1) * page_count]
