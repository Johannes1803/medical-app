from typing import Sequence


def paginate(collection_: Sequence, offset: int = 0, limit: int = 10) -> Sequence:
    """Return paginated range of collection.

    :param collection_: indexable sequence of objects
    :param offset: return elements starting from offset index position
    :param limit: maximum number of elements to return,
            actual returned number can be lower if there are less elements in collection after offset.
    :return: collection from offset to offest + limit
    """
    end_index = offset + limit
    return collection_[offset:end_index]
