import functools

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
                 frozen=NOTHING):
        self.type = type
        self.default = default
        self.validators = []
        if type:
            self.validators.append(functools.partial(isinstance, A_tuple=type))
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
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if getattr(instance.__class__, '__frozen__', False) and \
                getattr(instance, '__initialized__', False):
            raise AttributeError('Can not set attribute!')
        for validate in self.validators:
            if not validate(value):
                raise ValueError(f'Incorrect value {value} for {self.name}')
        instance.__dict__[self.name] = value


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

    def __hash__(self):
        hash_attr_names = (a.name for a in self.__attrs__ if a.hash)
        hash_items = [self.__class__.__module__, self.__class__.__name__]
        for attr_name in hash_attr_names:
            hash_items.append(getattr(self, attr_name, NOTHING))
        return hash(tuple(hash_items))


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
