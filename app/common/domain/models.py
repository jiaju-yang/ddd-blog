from ddd import ValueObject, Attr

from .registries import services


class Id(ValueObject):
    value: int = Attr()

    @classmethod
    def next(cls):
        return cls(services.generate_unique_id())
