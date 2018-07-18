from .validators import instance_of, not_none


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
            self.validators.append(not_none())
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


class Attrs:
    def __init__(self, attrs=()):
        self._all = {a.name: a for a in attrs}

    @property
    def required_attr_names(self):
        return tuple(a.name for a in self._all.values() if a.is_required)

    @property
    def all_attr_names(self):
        return tuple(a.name for a in self._all.values())

    @property
    def hash_attr_names(self):
        return tuple(a.name for a in self._all.values() if a.hash)

    @property
    def has_default_attrs(self):
        return tuple(a for a in self._all.values() if not a.is_required)

    def __getitem__(self, item):
        return self._all[item]

    def get(self, key, default=None):
        return self._all.get(key, default)


class ModelMeta(type):
    def __new__(mcs, typename, bases, attr_dict):
        cls = super().__new__(mcs, typename, bases, attr_dict)
        attrs = mcs._traverse_attrs(cls)
        cls.__attrs__ = Attrs(attrs)
        for a in attrs:
            delattr(cls, a.name)
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
