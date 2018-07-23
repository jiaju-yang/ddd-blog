from unittest.mock import patch

import pytest

from app.common.domain.models import Id


class TestId:
    @pytest.fixture(scope='class')
    def AId(self):
        class AId(Id):
            pass

        return AId

    def test_id_instantiation(self, AId):
        with pytest.raises(ValueError):
            AId('a')

        with pytest.raises(ValueError):
            AId(None)

        aid = AId(1)
        assert aid.value == 1

    @patch('app.common.domain.registries.services.generate_unique_id', side_effect=lambda: 1)
    def test_next(self, _, AId):
        aid = AId.next()
        another_id = AId(1)
        assert aid == another_id
