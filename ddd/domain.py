import abc
from itertools import chain

from .make import ModelMeta, NOTHING, Attrs


class DomainModel(metaclass=ModelMeta):
    def __init__(self, *args, **kwargs):
        pos_args = dict(zip(self._attrs, args))
        all_args = {**pos_args, **kwargs}

        duplicated_args = set(pos_args.keys()) & set(kwargs.keys())
        if duplicated_args:
            raise TypeError(f"__init__() got multiple values for argument "
                            f"'{', '.join(duplicated_args)}'")

        missing_required_attrs = set(self._required_attrs) - set(
            all_args.keys())
        if missing_required_attrs:
            raise TypeError(
                f"__init__() missing {len(missing_required_attrs)} required "
                f"positional argument: "
                f"'{', '.join(missing_required_attrs)}'")

        redundant_attrs = set(all_args) - set(self._attrs)
        if redundant_attrs:
            raise TypeError(
                f"__init__() got an unexpected keyword argument "
                f"'{', '.join(tuple(redundant_attrs))}'")

        has_default_attrs = self.__has_default_attrs
        for a in has_default_attrs:
            if a.name not in all_args:
                all_args[a.name] = a.default()

        for key, value in all_args.items():
            setattr(self, key, value)
        self.__initialized__ = True

    def __repr__(self):
        attrs_pair = []
        for a in self._attrs:
            attrs_pair.append(('{}={}'.format(
                a, repr(getattr(self, a, NOTHING)))))
        result = [self.__class__.__name__, '(', ', '.join(attrs_pair), ')']
        return ''.join(result)

    def _asdict(self, **rename):
        result = {}
        for a in self._attrs:
            value = getattr(self, a)
            name = rename.get(a) or a
            if isinstance(value, DomainModel):
                result[name] = value._asdict()
            else:
                result[name] = value
        return result

    def __iter__(self):
        yield from (getattr(self, attr) for attr in self._attrs)

    def __setattr__(self, key, value):
        attr = next((ac[key] for ac in self.__attrs_containers()
                     if ac.get(key)), None)
        if attr:
            if getattr(self.__class__, '__frozen__', False) and \
                    getattr(self, '__initialized__', False):
                raise AttributeError('Can not set attribute!')
            for validate in attr.validators:
                if not validate(self, value):
                    raise ValueError(
                        f"Incorrect value '{value}' for attribute '{attr.name}'"
                        f" in '{self.__class__.__name__}' object")
        super().__setattr__(key, value)

    @property
    def _attrs(self):
        return self.__attrs_by_condition('all_attr_names')

    @property
    def _required_attrs(self):
        return self.__attrs_by_condition('required_attr_names')

    @property
    def _hash_attrs(self):
        return self.__attrs_by_condition('hash_attr_names')

    @property
    def __has_default_attrs(self):
        return self.__attrs_by_condition('has_default_attrs')

    @classmethod
    def __attrs_by_condition(cls, condition):
        return tuple(chain.from_iterable(getattr(ac, condition)
                                         for ac in cls.__attrs_containers()))

    @classmethod
    def __attrs_containers(cls):
        none_attrs = Attrs()
        return (
            getattr(cls, '__attrs__', none_attrs)
            for cls in reversed(cls.__mro__[: -1])
        )


class Entity(DomainModel):
    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class ValueObject(DomainModel):
    __frozen__ = True

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        for a in self._attrs:
            if getattr(self, a) != getattr(other, a):
                return False
        return True

    def __hash__(self):
        hash_items = [self.__class__]
        for a in self._hash_attrs:
            hash_items.append(getattr(self, a, NOTHING))
        return hash(tuple(hash_items))

    def _new(self, **kwargs):
        new = {a: getattr(self, a) for a in self._attrs}
        new.update(kwargs)
        return self.__class__(**new)


class Repo(abc.ABC):
    pass
