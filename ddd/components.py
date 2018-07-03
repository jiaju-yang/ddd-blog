from itertools import chain

from .validators import instance_of, not_none

__all__ = ('Attr', 'DomainModel', 'ValueObject', 'Entity')


class _Nothing(object):
    """
    Sentinel class to indicate the lack of a value when ``None`` is ambiguous.

    All instances of `_Nothing` are equal.
    """

    def __copy__(self):
        return self

    def __deepcopy__(self, _):
        return self

    def __eq__(self, other):
        return other.__class__ == _Nothing

    def __repr__(self):
        return "NOTHING"

    def __hash__(self):
        return 0xc0ffee


NOTHING = _Nothing()


class Attr:
    def __init__(self,
                 type=None,
                 default=NOTHING,
                 validator=None,
                 hash=True,
                 name=None,
                 allow_none=False):
        self.name = name
        self.allow_none = allow_none
        self.hash = hash
        self.default = Factory(default)

        self.validators = []
        if not allow_none:
            self.validators.append(not_none)
        self.type = type
        if isinstance(validator, (tuple, list)):
            for validate in validator:
                if not callable(validate):
                    raise TypeError('Validator should be callable!')
            self.validators.extend(validator)
        elif validator:
            if not callable(validator):
                raise TypeError('Validator should be callable!')
            self.validators.append(validator)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return instance.__dict__[self.name]
        except KeyError:
            return self.default()

    def __set__(self, instance, value):
        if getattr(instance.__class__, '__frozen__', False) and \
                getattr(instance, '__initialized__', False):
            raise AttributeError('Can not set attribute!')
        for validate in self.validators:
            if not validate(instance, value):
                raise ValueError(
                    f"Incorrect value '{value}' for attribute '{self.name}' in "
                    f"'{instance.__class__.__name__}' object")
        instance.__dict__[self.name] = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        if type is not None:
            self.validators.append(instance_of(type))
        self._type = type

    @property
    def is_required(self):
        return not self.default.is_defined

    def validator(self, func):
        if not callable(func):
            raise TypeError('Validator should be callable!')
        self.validators.append(func)
        return func


class Factory:
    def __init__(self, default):
        if callable(default):
            self._factory = default
        else:
            self._default = default

    def __call__(self):
        if hasattr(self, '_factory'):
            return self._factory()
        else:
            return self._default

    @property
    def is_defined(self):
        return getattr(self, '_default', None) is not NOTHING


class _Attrs:
    def __init__(self, attrs=()):
        self._all = tuple(attrs)

    @property
    def required(self):
        return tuple(a.name for a in self._all if a.is_required)

    @property
    def all(self):
        return tuple(a.name for a in self._all)

    @property
    def hash(self):
        return tuple(a.name for a in self._all if a.hash)


class _ModelMeta(type):
    def __new__(mcs, typename, bases, attr_dict):
        cls = super().__new__(mcs, typename, bases, attr_dict)
        attrs = mcs._traverse_attrs(cls)
        cls.__attrs__ = _Attrs(attrs)
        return cls

    @staticmethod
    def _traverse_attrs(cls):
        annotations = getattr(cls, '__annotations__', {})
        potential_attrs = {name: value for name, value in cls.__dict__.items()
                           if isinstance(value, Attr) or name in annotations}
        attrs = []
        had_default = False
        for name, value in potential_attrs.items():
            if isinstance(value, Attr):
                attr = value
                attr.name = name
                if name in annotations:
                    if attr.type is not None:
                        raise ValueError(f"Duplicated type definition: {name}")
                    attr.type = annotations[name]
            else:
                attr = Attr(name=name, type=annotations[name],
                            default=cls.__dict__.get(name, NOTHING))

            if had_default and attr.is_required:
                raise ValueError(
                    "No mandatory attributes allowed after an attribute "
                    "with a default value or factory. Attribute in "
                    f"question: {name}")
            elif not had_default and not attr.is_required:
                had_default = True

            if (attr.type and attr.default.is_defined) and not isinstance(
                    attr.default(), attr.type):
                raise ValueError(
                    f'Incorrect attribute type and default value: {attr.name}')

            attrs.append(attr)

        return tuple(attrs)


class DomainModel(metaclass=_ModelMeta):
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

    @property
    def _attrs(self):
        return tuple(chain.from_iterable(a.all
                                         for a in self.__attr_descriptors()))

    @property
    def _required_attrs(self):
        return tuple(chain.from_iterable(a.required
                                         for a in self.__attr_descriptors()))

    @property
    def _hash_attrs(self):
        return tuple(chain.from_iterable(a.hash
                                         for a in self.__attr_descriptors()))

    @classmethod
    def __attr_descriptors(cls):
        none_attrs = _Attrs()
        return (
            getattr(cls, '__attrs__', none_attrs)
            for cls in reversed(cls.__mro__[: -1])
        )


class Entity(DomainModel):
    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        return self.id == other.id


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
