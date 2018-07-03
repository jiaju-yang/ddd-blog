from unittest.mock import patch

import pytest

from app.common.domain.models import Id


class TestId:
    def test_id_instantiation(self):
        with pytest.raises(ValueError):
            Id('a')

        with pytest.raises(ValueError):
            Id(None)

        id = Id(1)
        assert id.value == 1

    @patch('app.common.domain.models.generate_unique_id', side_effect=lambda: 1)
    def test_next(self, _):
        aid = Id.next()
        another_id = Id(1)
        assert aid == another_id
