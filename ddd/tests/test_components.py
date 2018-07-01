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

    def test_instantiate_inherited_object(self):
        class GrandmaVO(ValueObject):
            a = Attr()
            b = Attr()

        class FatherVO(GrandmaVO):
            c = Attr()
            d = Attr()

        class MotherVO(GrandmaVO):
            e = Attr()
            f = Attr()

        class ChildVO(MotherVO, FatherVO):
            g = Attr()
            h = Attr()

        avo = ChildVO(1, 2, 3, 4, 5, 6, 7, 8)
        assert tuple(avo) == (1, 2, 3, 4, 5, 6, 7, 8)

    def test_annotation_instantiation(self):
        class AVO(ValueObject):
            a: int = Attr()
            b: str = Attr()
            c: str
            d: int = 1

        avo = AVO(1, 'x', 'y')
        assert tuple(avo) == (1, 'x', 'y', 1)

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

    def test_factory_of_default_attribute(self):
        class AVO(ValueObject):
            a = Attr(default=5)
            b = Attr(default=list)

        avo = AVO()
        another_vo = AVO()
        assert avo.a == 5
        assert avo.b == another_vo.b == []
        assert avo.b is not another_vo

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

    def test_redundant_attr_instantiation(self):
        class AVO(ValueObject):
            a = Attr()

        with pytest.raises(TypeError):
            AVO(1, b=2)

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

        avo = AVO('x', 1, 2.1, ('k',), {'k': 'v'}, ['k'], {'k'}, AnotherVO('c'))
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

    def test_asdict_rename(self):
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
        assert avo._asdict(g='i', h='j') == {
            'a': 'x',
            'b': 1,
            'c': 2.1,
            'd': ('k',),
            'e': {'k': 'v'},
            'f': ['k'],
            'i': {'k'},
            'j': {'x': 'c'}
        }

    def test_iterable(self):
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
        assert tuple(avo) == (
            'x', 1, 2.1, ('k',), {'k': 'v'}, ['k'], {'k'}, AnotherVO(x='c'))

    def test_new(self):
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
        new = avo._new(c=3)

        assert avo.c == 2.1
        assert new.c == 3
        assert avo is not new

        with pytest.raises(TypeError):
            avo._new(i=1)

    def test_immutable(self):
        class AVO(ValueObject):
            a = Attr()
            b = Attr()

        avo = AVO(1, 2)
        with pytest.raises(AttributeError):
            avo.a = 3

    def test_attrs(self):
        class GrandmaVO(ValueObject):
            a = Attr()
            b = Attr()

        class FatherVO(GrandmaVO):
            c = Attr()
            d = Attr()

        class MotherVO(GrandmaVO):
            e = Attr()
            f = Attr()

        class ChildVO(MotherVO, FatherVO):
            g = Attr()
            h = Attr()

        vo = ChildVO(1, 2, 3, 4, 5, 6, 7, 8)
        assert vo._attrs == ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
