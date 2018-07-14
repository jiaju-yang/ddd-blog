def instance_of(type):
    return lambda instance, value: value is None or isinstance(value, type)


def not_none():
    return lambda instance, value: value is not None
