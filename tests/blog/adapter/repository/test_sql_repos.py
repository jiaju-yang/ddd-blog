import pytest

from app.blog.adapter.repository.sql.repos import SqlTagRepo
from app.blog.domain.models import Tag, TagId
from tests.common.helpers import SqlEnvironment


class TestUserRepo(SqlEnvironment):
    @pytest.fixture(scope='class')
    def repo(self):
        return SqlTagRepo()

    @pytest.fixture(scope='function')
    def mock_tag(self):
        return Tag(TagId.next(), 'life')

    @pytest.fixture(scope='function')
    def another_mock_tag(self):
        return Tag(TagId.next(), 'coding')

    def test_save_one_tag(self, repo, mock_tag):
        repo.save(mock_tag)
        saved_tag = repo.all()
        assert len(saved_tag) == 1
        assert saved_tag[0].id == mock_tag.id
        assert saved_tag[0].name == mock_tag.name

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
