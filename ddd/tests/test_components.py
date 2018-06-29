from ddd import Attr, DomainModel, ValueObject


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

    def test_repr(self):
        class AVO(DomainModel):
            x = Attr()
            y = Attr()
            z = Attr()

        avo = AVO('a', 1, ['b'])
        assert repr(avo) == """AVO(x='a', y=1, z=['b'])"""
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
