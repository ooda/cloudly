import copy


def merge(dict1, dict2):
    """Merge two dicts.
    When merging, if two dicts have the same key, they are combined to form a
    new dict:

        d1 = {'a': {'b': 1}, 'b': 4, 'c': {'b': 2}}
        d2 = {'a': {'c': 2, 'g': {'a': 2}}, 'c': {'g': 6}, 'd': 4}

        merged = {
            'a': {'b': 1, 'c': 2, 'g': {'a': 2}},
            'b': 4,
            'c': {'b': 2, 'g': 6},
            'd': 4
        }

    There is one restriction: common keys *must* have dict-like values.
    """
    keys1, keys2 = dict1.viewkeys(), dict2.viewkeys()
    intersection = keys1 & keys2
    # if dict1 and dict2 have no commons keys, it's easy: just update
    if not intersection:
        merged = copy.deepcopy(dict1)
        merged.update(dict2)
        return merged
    else:
        # When common keys are present, call itself recursively with both
        # values as the new dicts.
        merged = {}
        for key in intersection:
            if (type(dict1[key]) is dict) and (type(dict2[key]) is dict):
                merged[key] = merge(dict1[key], dict2[key])
            else:
                raise ValueError("Common keys must have dict-like values.")
        # Then merge keys that are *not* common to both.
        for key in keys1 - keys2:
            merged[key] = dict1[key]
        for key in keys2 - keys1:
            merged[key] = dict2[key]

        return merged


def find_item(keys, d, create=False):
    """Return a possibly deeply buried {key, value} with all parent keys.

    Given:

        keys = ['a', 'b']
        d = {'a': {'b': 1, 'c': 3}, 'b': 4}

    returns:

        {'a': {'b': 1}}

    """
    default = {} if create else None
    value = d.get(keys[0], default)
    if len(keys) > 1 and type(value) is dict:
        return {keys[0]: find_item(keys[1:], value, create)}
    else:
        return {keys[0]: value}


def find_value(keys, d, create=False):
    """Return a possibly deeply buried {key, value} with all parent keys.

    Given:

        keys = ['a', 'b']
        d = {'a': {'b': 1, 'c': 3}, 'b': 4}

    returns: 1
    """
    default = {} if create else None
    value = d.get(keys[0], default)
    if len(keys) > 1 and type(value) is dict:
        return find_value(keys[1:], value, create)
    else:
        return value
