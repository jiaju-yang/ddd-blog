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
                 hash=True):
        self.type = type
        self.default = default
        self.validators = []
        if type:
            self.validators.append(
                lambda instance, value: isinstance(value, type))
        if isinstance(validator, (tuple, list)):
            for validate in validator:
                if not callable(validate):
                    raise TypeError('Validator should be callable!')
            self.validators.extend(validator)
        elif validator:
            if not callable(validator):
                raise TypeError('Validator should be callable!')
            self.validators.append(validator)
        self.hash = hash
        self.name = None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return instance.__dict__[self.name]
        except KeyError:
            return self.default

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
    def is_required(self):
        return self.default is NOTHING

    def validator(self, func):
        if not callable(func):
            raise TypeError()
        self.validators.append(func)
        return func


class _ClassBuilder:
    def __init__(self, cls):
        self._cls = cls
        self._attrs = self._traverse_attrs(cls)
        self._cls_dict = {
            '__attrs__': self._attrs,
        }

    def build_class(self):
        cls = self._cls
        for name, value in self._cls_dict.items():
            setattr(cls, name, value)
        return cls

    @staticmethod
    def _traverse_attrs(cls):
        attrs = []
        had_default = False
        for name, attr in cls.__dict__.items():
            if isinstance(attr, Attr):
                if had_default and attr.default is NOTHING:
                    raise ValueError(
                        "No mandatory attributes allowed after an attribute "
                        "with a default value or factory. Attribute in "
                        f"question: {name}")
                elif not had_default and attr.default is not NOTHING:
                    had_default = True
                attr.name = name
                attrs.append(attr)
        return tuple(attrs)


class _ModelMeta(type):
    def __new__(mcs, typename, bases, attr_dict):
        cls = super().__new__(mcs, typename, bases, attr_dict)
        builder = _ClassBuilder(cls)
        return builder.build_class()


class DomainModel(metaclass=_ModelMeta):
    def __init__(self, *args, **kwargs):
        pos_args = {a.name: value for a, value in zip(self.__attrs__, args)}
        all_args = {**pos_args, **kwargs}

        duplicated_args = set(pos_args.keys()) & set(kwargs.keys())
        if duplicated_args:
            raise TypeError(f"__init__() got multiple values for argument "
                            f"'{', '.join(duplicated_args)}'")

        missing_required_attrs = set(self._required_attrs()) - set(
            all_args.keys())
        if missing_required_attrs:
            raise TypeError(
                f"__init__() missing {len(missing_required_attrs)} required "
                f"positional argument: "
                f"'{', '.join(missing_required_attrs)}'")

        for key, value in all_args.items():
            setattr(self, key, value)
        self.__initialized__ = True

    def __repr__(self):
        attrs_pair = []
        for a in self.__attrs__:
            attrs_pair.append(('{}={}'.format(
                a.name, repr(getattr(self, a.name, NOTHING)))))
        result = [self.__class__.__name__, '(', ', '.join(attrs_pair), ')']
        return ''.join(result)

    def _asdict(self, **rename):
        result = {}
        for a in self.__attrs__:
            value = getattr(self, a.name)
            if isinstance(value, DomainModel):
                result[a.name] = value._asdict()
            else:
                result[a.name] = value
        return result

    @classmethod
    def _default_attrs(cls):
        return tuple(a.name for a in cls.__attrs__ if not a.is_required)

    @classmethod
    def _required_attrs(cls):
        return tuple(a.name for a in cls.__attrs__ if a.is_required)


class Entity(DomainModel):
    pass


class ValueObject(DomainModel):
    __frozen__ = True

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False
        for a in self.__attrs__:
            if getattr(self, a.name) != getattr(other, a.name):
                return False
        return True

    def __hash__(self):
        hash_attr_names = (a.name for a in self.__attrs__ if a.hash)
        hash_items = [self.__class__]
        for attr_name in hash_attr_names:
            hash_items.append(getattr(self, attr_name, NOTHING))
        return hash(tuple(hash_items))
