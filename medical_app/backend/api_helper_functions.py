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


def convert_camel_case_to_underscore(camel_case_name: str) -> str:
    """Convert camel case var name to underscore python convention var name.

    :param camel_case_name: var in camel case
    :return same var name in under score
    """
    under_score_var_name = ""
    for char in camel_case_name:
        if char.isupper():
            under_score_var_name += "_" + char.lower()
        else:
            under_score_var_name += char
    return under_score_var_name
