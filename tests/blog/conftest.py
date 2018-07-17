from datetime import datetime

import pytest

from app.blog.domain.models import Tag, TagId, Article, ArticleId, Author


@pytest.fixture(scope='function')
def mock_tag():
    return Tag(TagId(1), 'life')


@pytest.fixture(scope='function')
def another_mock_tag():
    return Tag(TagId(2), 'coding')


@pytest.fixture(scope='function')
def mock_article(mock_tag, another_mock_tag):
    return Article(ArticleId(1), 'A Title', "article's content",
                   Author(1, 'psyche'),
                   datetime(year=2018, month=7, day=15), None, None,
                   tags=[mock_tag, another_mock_tag])


@pytest.fixture(scope='function')
def another_mock_article(mock_tag):
    return Article(ArticleId(2), 'Another Title', "other article's content",
                   Author(1, 'psyche'),
                   datetime(year=2018, month=7, day=15), None, None,
                   tags=[mock_tag])
