from typing import List

import pytest

from app.blog.adapter.repositories.sql.repos import SqlTagRepo, SqlArticleRepo
from tests.common.helpers import SqlEnvironment


class TestUserRepo(SqlEnvironment):
    @pytest.fixture(scope='class')
    def repo(self):
        return SqlTagRepo()

    def test_save_one_tag(self, repo, mock_tag):
        repo.save(mock_tag)
        saved_tags = repo.all()
        assert len(saved_tags) == 1
        assert saved_tags[0].id == mock_tag.id
        assert saved_tags[0].name == mock_tag.name

    def test_save_one_tag_twice(self, repo, mock_tag):
        repo.save(mock_tag)
        new_name = 'love'
        mock_tag.name = new_name
        repo.save(mock_tag)
        saved_tags = repo.all()
        assert len(saved_tags) == 1
        assert saved_tags[0].id == mock_tag.id
        assert saved_tags[0].name == new_name

    def test_save_two_tags(self, repo, mock_tag, another_mock_tag):
        repo.save(mock_tag)
        repo.save(another_mock_tag)
        assert len(repo.all()) == 2

    def test_all(self, repo, mock_tag, another_mock_tag):
        repo.save(mock_tag)
        saved_tags = repo.all()
        assert len(saved_tags) == 1
        assert isinstance(saved_tags, List)

        repo.save(another_mock_tag)
        saved_tags = repo.all()
        assert len(saved_tags) == 2


class TestArticleRepo(SqlEnvironment):
    @pytest.fixture(scope='class')
    def repo(self):
        return SqlArticleRepo()

    def test_save_one_article(self, repo, mock_article):
        repo.save(mock_article)
        saved_articles = repo.recently_articles_of_page()
        assert len(saved_articles) == 1
        saved_article = saved_articles[0]
        assert saved_article.id == mock_article.id
        assert saved_article.title == mock_article.title
        assert saved_article.content == mock_article.content
        assert saved_article.author == mock_article.author
        assert saved_article.created_at == mock_article.created_at
        assert saved_article.updated_at is None
        assert saved_article.deleted_at is None
        assert saved_article.tags == mock_article.tags

    def test_save_one_article_twice(self, repo, mock_article):
        repo.save(mock_article)
        new_title = 'New Title'
        mock_article.title = new_title
        repo.save(mock_article)
        saved_articles = repo.recently_articles_of_page()
        assert len(saved_articles) == 1
        assert saved_articles[0].id == mock_article.id
        assert saved_articles[0].title == new_title

    def test_save_two_articles(self, repo, mock_article, another_mock_article):
        repo.save(mock_article)
        repo.save(another_mock_article)
        assert len(repo.recently_articles_of_page()) == 2

    def test_recently_articles_of_page(
            self, repo, mock_article, another_mock_article):
        repo.save(mock_article)
        repo.save(another_mock_article)
        saved_articles = repo.recently_articles_of_page(page=0, page_count=1)
        assert len(saved_articles) == 1
        assert isinstance(saved_articles, List)
        assert saved_articles[0].id == mock_article.id

        saved_articles = repo.recently_articles_of_page(page=1, page_count=1)
        assert len(saved_articles) == 1
        assert saved_articles[0].id == another_mock_article.id
