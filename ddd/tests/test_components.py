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

        class AnotherVO(ValueObject):
            a = Attr()

        assert hash(AVO('x')) != hash(AVO('y'))
        assert hash(AVO('x')) == hash(AVO('x'))
        assert hash(AVO('x')) != hash(AnotherVO('x'))

    def test_repr(self):
        class AVO(ValueObject):
            a = Attr()
            b = Attr()
            c = Attr()

        avo = AVO('x', 1, ['y'])
        assert repr(avo) == """AVO(a='x', b=1, c=['y'])"""

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
