"""
This private module contains discontinued functions, tests and broken stuff
that was used or tested for the search engine matching and rating algorithms.
Functions are yet to be deleted but are NOT used anywhere and kept for reference
while developing.
"""
# flake8: noqa
from search import config, utils


def similarity(query, string):
    """
    Calculate the match for the given `query` and `string`.

    The match is calculated using the `jaro winkler` for each set of the matrix
    (`query` x `string`) and takes into consideration the position difference
    into the strings.

    Arguments:
        query (str): search query
        string (str): string to test against

    Returns:
        float: normalized value indicating the probability of match, where
        0 means completely dissimilar and 1 means equal.
    """

    # split the two strings cleaning out some stuff
    query = utils.tokenize(query)
    string = utils.tokenize(string)

    # if one of the two strings is falsy (no content, or was passed with items
    # short enough to be trimmed out), return 0 here to avoid ZeroDivisionError
    # later on while processing.
    if len(query) == 0 or len(string) == 0:
        return 0

    short, long_ = sorted((query, string), key=lambda x: len(x))

    matches = {}
    # generate a matrix from the two strings and loop on every couple
    for string1, string2 in ((s1, s2) for s1 in long_ for s2 in short):
        # get the jaro winkler equality between the two strings
        match = utils.ratio(string1, string2)
        # calculate the distance factor for the position of the segments
        # on their respective lists
        positional = position_similarity(string1, string2, long_, short)

        # get them together and append to the matches dictionary
        matches.setdefault(string1, []).append((match, positional))

    # get the highest value for each list, the apply the word-distance factor
    # the key takes the jaro winkler distance value to get the max value
    matches = [max(m, key=lambda x: x[0]) for m in matches.values()]
    weights_ = utils.scale_to_one((config.MATCH_WEIGHT, config.DIST_WEIGHT))
    matches = [utils.weighted_average((m, d), weights_) for m, d in matches]

    # get the weighted mean for all the highest matches and apply the highest
    # match value found as coefficient as multiplier, to add weights to more
    # coherent matches.
    weights_ = list(range(len(matches), 0, -1))
    return utils.weighted_average(matches, weights_) * max(matches)


# =====================================================================
# Positional similarity


def position_similarity(el1, el2, seq1, seq2):
    """
    Get the normalized inverted movement cost for for between `el1` and
    `el2` on the `seq2` iterable.

    The function is used to get a value describing how far two words are in a
    phrase (as list, as in ``string.split(' ')`` or, in our case through
    :func:`search.utils.tokenize`).

    Moves are relative to el1 on seq1, which `should` be the longest set
    for the function to work properly.

    .. warning::
        The function is currently broken and always returns 1, making
        the position inside the matching string irrelevant.

    .. note:: The given strings **MUST** be inside the corresponding list.

    Arguments:
        el1 (any): element of the ``seq1`` iterable
        el2 (any): element of the ``seq2`` iterable
        seq1 (iterable): iterable allowing the ``index`` method containing
            the `el1` element.
        seq2 (iterable): iterable allowing the ``index`` method containing
            the `el2` element.

    Returns:
        float: value ``0 -> 1`` representing how far the two words are,
        where ``1`` represent the closest(same position) and tending to zero
        the farthest on the maximum available moves possible on ``seq1``.

    """
    return 1
    # FIXME: Something's wrong here.
    # Function left `on hold` with a return 1 since we need a value and 1
    # should be the default value for "everything is where is supposed to be"
    # -------------------------------------------------------------------------
    # The function SHOULD return a value representing a ratio of word (el1)
    # position inside the sequence that contains it (seq1) relative to the
    # other element (el2) on its sequence (seq2).
    # The reason for this function to exist is to have a value that tells the
    # rest of the search algoritm how much an element is offset relative to
    # the supposed position, allowing the search to give more weight to
    # queries that are written exactly as they are found, while i.e. inverted
    # order should have little less weight.
    # The idea is to have a 1 when:
    # * len(seq1) == len(seq2) AND indexes of elements are the same:
    #       'hi, hello there', 'yo, hello world' -> ('there', 'world')
    # * lengths are different BUT the el1 is proportionally at about the same
    #   position in seq1 as el2 is on el2:
    #       'hello world, 'hello there, how are you' -> ('world', 'are')
    #   meaning that the elements are more or less in the same "spot".
    # * one of the two sequences have length 1:
    #   should be irrelevant any type of calculus since the relative position
    #   of such word will be 0 (index/length) or the reciprocal will be 1
    #   (1 - idx/len)
    #
    # All other cases should return a value between 1 and ->0, tending toward
    # 0 the more the longest sequence is long.
    # =========================================================================

    long_, short = seq1, seq2
    el_long, el_short = el1, el2
    len_long, len_short = len(seq1), len(seq2)

    if len_long == 1 or len_short == 1:
        # useless to count as this would
        # * cause a ZeroDivisionError (no moves available)
        # * return 1 in any case since the algorithm NEEDS to return 1 if one
        #   of the two sequence is of len 1
        return 1

    if len_short > len_long:
        # Reverse if needed
        # NOTE: This should be ok and would prevent dumbness when setting up
        # the function call
        long_, short = short, long_
        el_long, el_short = el_short, el_long
        len_long, len_short = len_short, len_long

    long_idx = long_.index(el_long)
    short_idx = short.index(el_short)
    moves = abs(long_idx - short_idx)
    max_moves = max_distance(long_, word_index=long_idx)

    return abs(1 - (moves / max_moves))


def max_distance(sequence, idx):
    """
    Given a list an int in range(len(sequence)), determine the maximum
    amount of `movements` available from that index position in the list.

    Arguments:
        sequence(any with __len__): iterable to calculate the maximum moves
            into. It's used only to get its `len`, so any object that
            implements the `__len__` method will do.
        idx(int): index to count from.
            The value ** must ** be `>= 0` but ** can ** be over the length
            of the list.

    Returns:
        int: maximum moves available in any direction.

    Example:
        >>> utils.get_max_moves(['a', 'b', 'c', 'd', 'e'], 1)
        4  # index 1 -> 'b', so max is 4 moves right
        >>> utils.get_max_moves(['a', 'b', 'c', 'd', 'e'], 6)
        5  # can move left 5
    """

    return max(idx, (len(sequence) - (idx + 1)))

# =====================================
# Test utils


def test_max_distance(self):
    l1 = ['a', 'b', 'c', 'd']
    l2 = ['a', 'b', 'c', 'd', 'e']

    assert 2 == utils.max_distance(l1, 1)  # l1.b
    assert 2 == utils.max_distance(l1, 2)  # l1.c
    assert 3 == utils.max_distance(l2, 1)  # l2.b
    assert 4 == utils.max_distance(l2, 4)  # l2.e


def _test_position_similarity(self):
    # FIXME: The function is broken, but for continuity the test remains
    # with all `falsy` results checked.
    q, s = 'pinco'.split(' '), 'guerra pinco pallo'.split(' ')

    assert 1 == matchers.position_similarity(
        'pinco', 'guerra', q, s)  # 0,0
    assert 1 == matchers.position_similarity(
        'pinco', 'pinco', q, s)   # 0,1

    q = 'pallo pinco'.split(' ')
    assert 1 == matchers.position_similarity(
        'pallo', 'guerra', q, s)  # 0,1
    assert 1 == matchers.position_similarity(
        'pinco', 'guerra', q, s)  # 1,0
    assert 1 == matchers.position_similarity(
        'pinco', 'pinco', q, s)   # 1,1
    assert 1 == matchers.position_similarity(
        'pallo', 'guerra', q, s)  # 0,0

    q = 'hello world is it a sunny out there'
    s = 'hello there it is a sunny world'
    q, s = q.split(' '), s.split(' ')

    assert 1 == matchers.position_similarity('world', 'there', q, s)  # 1,1
    assert 1 == matchers.position_similarity('hello', 'world', q, s)  # 0,6
    assert 1 == matchers.position_similarity('there', 'world', q, s)  # 8,1
    assert 1 == matchers.position_similarity('it', 'it', q, s)        # 4,3
    assert 1 == matchers.position_similarity('hello', 'is', q, s)     # 0,3
