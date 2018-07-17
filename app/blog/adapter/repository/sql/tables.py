from app.common.adapter.repository.sql import db
from ....domain.models import Author, Tag, TagId, Article, ArticleId

tag = db.Table(
    'tag',
    db.Column('id', db.BigInteger, primary_key=True, unique=True, key='__id'),
    db.Column('name', db.String(50), unique=True)
)

TagId.__composite_values__ = lambda self: (self.value,)

db.mapper(Tag, tag, properties={
    'id': db.composite(TagId, tag.c.__id),
})

article = db.Table(
    'article',
    db.Column('id', db.BigInteger, primary_key=True, unique=True, key='__id'),
    db.Column('title', db.String(100)),
    db.Column('content', db.Text),
    db.Column('author_id', db.BigInteger, key='__author_id'),
    db.Column('author_name', db.String(50), key='__author_name'),
    db.Column('created_at', db.DateTime(timezone=True)),
    db.Column('updated_at', db.DateTime(timezone=True)),
    db.Column('deleted_at', db.DateTime(timezone=True)),
)

ArticleId.__composite_values__ = lambda self: (self.value,)
Author.__composite_values__ = lambda self: (self.id, self.name)

tag_article_association = db.Table(
    'tag_article_association',
    db.Column('tag_id', db.BigInteger, db.ForeignKey('tag.__id')),
    db.Column('article_id', db.BigInteger, db.ForeignKey('article.__id'))
)

db.mapper(Article, article, properties={
    'id': db.composite(ArticleId, article.c.__id),
    'author': db.composite(
        Author, article.c.__author_id, article.c.__author_name),
    'tags': db.relationship(Tag, secondary=tag_article_association)
})
