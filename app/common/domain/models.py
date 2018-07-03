from ddd import ValueObject, Attr
from ..adapter.services import generate_unique_id


class Id(ValueObject):
    value: int = Attr()

    @classmethod
    def next(cls):
        return cls(generate_unique_id())
