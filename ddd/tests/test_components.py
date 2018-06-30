import numbers

import pytest

from ddd import Attr, ValueObject


class TestValueObject:
    def test_correct_instantiation(self):
        class AVO(ValueObject):
            a = Attr()
            b = Attr()
            c = Attr()
            d = Attr()
            e = Attr()
            f = Attr()
            g = Attr()
            h = Attr()

        class AnotherVO(ValueObject):
            x = Attr()

        avo = AVO('x', 1, 2.1, ('k',), {'k': 'v'}, ['k'], {'k'}, AnotherVO('c'))
        assert avo.a == 'x'
        assert avo.b == 1
        assert avo.c == 2.1
        assert avo.d == ('k',)
        assert avo.e == {'k': 'v'}
        assert avo.f == ['k']
        assert avo.g == {'k'}
        assert avo.h == AnotherVO('c')

    def test_default_attribute(self):
        class AVO(ValueObject):
            a = Attr()
            b = Attr(default=1)

        avo = AVO('x')
        assert avo.a == 'x'
        assert avo.b == 1

        avo = AVO('x', 2)
        assert avo.a == 'x'
        assert avo.b == 2

    def test_incorrect_default_order(self):
        with pytest.raises(ValueError):
            class AVO(ValueObject):
                a = Attr(default=5)
                b = Attr()

        with pytest.raises(ValueError):
            class AnotherVO(ValueObject):
                a = Attr()
                b = Attr(default=None)
                c = Attr()

    def test_duplicated_attr_instantiation(self):
        class AVO(ValueObject):
            a = Attr()
            b = Attr()
            c = Attr(default=1)

        with pytest.raises(TypeError):
            AVO('x', 'y', a='z')

        with pytest.raises(TypeError):
            AVO('x', 'y', b='z')

        with pytest.raises(TypeError):
            AVO('x', 'y', 2, c=3)

    def test_miss_required_attrs(self):
        class AVO(ValueObject):
            a = Attr()
            b = Attr()
            c = Attr(default=5)

        with pytest.raises(TypeError):
            AVO()

        with pytest.raises(TypeError):
            AVO(b=1, c=1)

        with pytest.raises(TypeError):
            AVO(1, c=1)

    def test_check_attr_type(self):
        class AVO(ValueObject):
            a = Attr(type=int)
            b = Attr(type=str)

        with pytest.raises(ValueError):
            AVO('x', 'y')

        with pytest.raises(ValueError):
            AVO(1, 1)

        with pytest.raises(ValueError):
            AVO('x', 1)

    def test_hash(self):
        class AVO(ValueObject):
            a = Attr()
            b = Attr(hash=False)

        class AnotherVO(ValueObject):
            a = Attr()
            b = Attr(hash=False)

        assert hash(AVO('x', 'y')) != hash(AVO('y', 'y'))
        assert hash(AVO('x', 'y')) == hash(AVO('x', 'z'))
        assert hash(AVO('x', 'y')) != hash(AnotherVO('x', 'y'))

    def test_eq(self):
        class AVO(ValueObject):
            a = Attr()
            b = Attr()

        class AnotherVO(ValueObject):
            a = Attr()
            b = Attr()

        vo1 = AVO('x', 'y')
        vo2 = AVO('x', 'y')
        another_vo = AnotherVO('x', 'y')

        assert vo1 == vo2
        assert vo1 is not vo2
        assert vo1 != another_vo
        assert vo1 is not another_vo

    def test_repr(self):
        class AVO(ValueObject):
            a = Attr()
            b = Attr()
            c = Attr()

        avo = AVO('x', 1, ['y'])
        assert repr(avo) == """AVO(a='x', b=1, c=['y'])"""

    def test_validator(self):
        class AVO(ValueObject):
            a = Attr(type=numbers.Real,
                     validator=lambda instance, value: 0 < value < 100)

        with pytest.raises(ValueError):
            AVO('x')

        with pytest.raises(ValueError):
            AVO(0)

        with pytest.raises(ValueError):
            AVO(100)

        AVO(99)

    def test_validator_decorator(self):
        class AVO(ValueObject):
            a = Attr()

            @a.validator
            def is_integer(self, value):
                if isinstance(value, numbers.Integral):
                    return True
                raise TypeError()

            @a.validator
            def between(self, value):
                return 0 < value < 100

        with pytest.raises(TypeError):
            AVO('c')

        with pytest.raises(ValueError):
            AVO(0)

        with pytest.raises(ValueError):
            AVO(100)

        AVO(99)

    def test_asdict(self):
        class AVO(ValueObject):
            a = Attr()
            b = Attr()
            c = Attr()
            d = Attr()
            e = Attr()
            f = Attr()
            g = Attr()
            h = Attr()

        class AnotherVO(ValueObject):
            x = Attr()

        avo = AVO('x', 1, 2.1, ('k',), {'k': 'v'}, ['k'], {'k'},
                  AnotherVO('c'))
        assert avo._asdict() == {
            'a': 'x',
            'b': 1,
            'c': 2.1,
            'd': ('k',),
            'e': {'k': 'v'},
            'f': ['k'],
            'g': {'k'},
            'h': {'x': 'c'}
        }

    # @pytest.fixture(scope='function')
    # def a_value_object(self):
    #     class AVO(ValueObject):
    #         a = Attr(type=int, default=1)
    #         b = Attr(type=str, required=True)
    #
    #         # def __init__(self, x, y, z):
    #         #     pass
    #
    #         # def __new__(cls, *args, **kwargs):
    #         #     pass
    #         # @validator
    #         # def x(self, value):
    #         #     if len(value) > 10:
    #         #         return False
    #
    #     return AVO('xxx', a=None, b=2, e='s')

    # def test_str(self):

    # def test_correct_instantiation(self, a_value_object):
    #     assert a_value_object.x == 1
    #     assert a_value_object.z == 's'
    #     assert a_value_object.y is None
    #     with pytest.raises(AttributeError):
    #         a_value_object.x = 2
    #     with pytest.raises(AttributeError):
    #         a_value_object.y = 2
    #
    # def test_replace(self, a_value_object):
    #     another_value_object = a_value_object._replace(y=3)
    #
    #     assert a_value_object.x == 1
    #     assert a_value_object.y is None
    #     assert another_value_object.x == 1
    #     assert another_value_object.y == 3
    #     assert a_value_object is not another_value_object
    #
    #     with pytest.raises(ValueError):
    #         a_value_object._replace(z=1)
