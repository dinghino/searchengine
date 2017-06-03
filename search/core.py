"""
Search API core module

Contains the main functions to get match values and searching
"""
from search import utils, config
from search.matchers import similarity


def search(
        query, attributes, dataset, limit=-1,
        threshold=config.THRESHOLD, weights=None):
    """
    Main function of the package, allows to do a fuzzy full-text search on the
    rows of the given `table` model, looking up the value
    on the given `attributes` list against the passed `query` string.

    Extra arguments allows some customization on the search results (see below)

    Arguments:
        query (str): String to search for
        attributes (list): The names of thetable columns to search into.
        dataset (iterable): iterable of `objects` to lookup. All the objects
            in the dataset **must** have the specified attribute(s)
        limit (int): max number of results to return. if ``-1`` will return
            everything.
        threshold (float): value under which results are considered not valid.
        weights (list): matching `attributes` argument, describes the
            attributes weights. if not provided **or** if different length
            the weight will generated automatically, considering
            the index of the attribute name, reversed (first -> more weight).

    Returns:
        list: A list containing ``[0:limit]`` resources from the given table,
        sorted by relevance.

    Raises:
        AttributeError: if one of the object does not have one of the given
            attribute(s).

    Example:
        Assuming a random number of items in the Item table, that defines
        `name`, `category`, `description`, `availability`, one can do:

        >>> from models import Item
        >>> from search import search
        >>> results = search('awesome', ['name', 'category'], Item.select())
        [<Item name: 'awesome item' cat: 'generic'>]

    .. note::
        Since this function implements the core functionality, it has the
        shortcut import

        >>> from search.core import search
        >>> from search import search

        Will have the same effect
    """
    matches = []
    if not weights or len(weights) != len(attributes):
        # list of integers of the same length of `attributes` as in [3, 2, 1]
        # for attributes = ['a', 'b', 'c']
        weights = list(range(len(attributes), 0, -1))

    weights = utils.scale_to_one(weights)
    weights = {attr: w for attr, w in zip(attributes, weights)}

    for obj in dataset:
        partial_matches = []

        for attr in attributes:
            attrval = getattr(obj, attr)

            match = similarity(query, attrval)
            partial_matches.append({'attr': attr, 'match': match})

        # get the highest match for each attribute and multiply it by the
        # attribute weight, so we can get the weighted average to return
        match = max(partial_matches, key=lambda m: m['match'])
        match = match['match'] * weights[match['attr']]

        if match >= threshold:
            matches.append({'data': obj, 'match': match})

    matches.sort(key=lambda m: m['match'], reverse=True)

    if limit > 0:
        matches = matches[:limit]

    return [m['data'] for m in matches]
