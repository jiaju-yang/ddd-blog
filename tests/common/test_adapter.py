import numbers

from app.common.adapter.services import generate_unique_id


class TestGenerateUniqueId:
    def test_id_type_is_int(self):
        assert isinstance(generate_unique_id(), numbers.Integral)

    def test_generate_different_id(self):
        assert generate_unique_id() != generate_unique_id()
