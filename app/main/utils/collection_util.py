def is_empty(collection: list):
    return collection is None or len(collection) == 0


def is_not_empty(collection: list):
    return is_empty(collection) is False
