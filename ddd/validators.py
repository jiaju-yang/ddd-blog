def instance_of(type):
    return lambda instance, value: value is None or isinstance(value, type)


def not_none(instance, value):
    return value is not None
