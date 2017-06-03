"""
Utility module for the search engine, contains various functions to do common
operations on lists and set of iterables
"""
import re
from search import config


def _dec(fl):
    """Return a stringified more readable float, for debugging purposes."""
    return '{:.2f}'.format(fl)


def splitter(string, chunk_size):
    """
    Generator function that returns chunks of `string` of size `chunk_size`.
    If chunk_size is ``-1`` the whole string is returned.

    Args:
        string (str): the string to get the chunks from
        chunk_size (int): max length of the chunks (last one can be shorter)

    Yields:
        one chunks of `string` of size `chunk_size` on each call such as

            >>> splitter('hello, world', 3)
            'hel', 'lo,', ' wo', 'rld'
    """
    l = len(string)
    if chunk_size <= 0 or l == 0 or chunk_size >= l:
        yield string

    i = 0
    while i < l:
        n, i = i, i + chunk_size
        yield string[n:i]


def slider(string, chunk_size):
    """
    Generator function that slides through a string and returns strings
    of (max) length `chunk_size`, sliding one character at a time.

    Args:
        string (str): the string to walk
        chunk_size (int): the size of each chunk

    Yield:
        one chunks of `string` of size `chunk_size` on each call such as

            >>> splitter('hello, world', 3)
            'hel', 'ell', 'llo', ...

    """
    i = 0
    while i <= len(string) - chunk_size:
        yield string[i:i + chunk_size]
        i += 1


def normalize(iterable):
    """
    Normalize an iterable of numbers in a series that sums up to 1.

    Arguments:
        iterable (numbers): an iterable containing numbers (either `int` or
            `float`) to normalize.

    Returns:
        list: Normalized float values, in the same order as the one provided.

    Example:
        >>> normalize([3, 2, 1])
        [0.5, 0.333333, 0.166667]

    """
    tot = sum(iterable)
    return [float(v) / tot for v in iterable]


def scale_to_one(iterable):
    """
    Scale an iterable of numbers proportionally such as the highest number
    equals to 1

    Example:
        >>> scale_to_one([5,4,3,2,1])
        [1, 0.8, 0.6, 0.4, 0.2]
    """
    m = max(iterable)
    return [v / m for v in iterable]


def weighted_average(values, weights):
    """Calculate the weighted mean average between two iterables of `values`
    and matching `weights`

    Args:
        values(iterable): Values to average, either `int` or `float`
        weights(iterable): Matching weights iterable

    Returns:
        float: weighted average

    """
    if len(values) != len(weights):
        raise ValueError(
            'Values and Weights length do not match for weighted average')
    val = sum(m * w for m, w in zip(values, weights))
    weights = sum(weights)
    return val / weights


def tokenize(string):
    """
    Given a string return a list of segments of the string,
    splitted with :any:`config.STR_SPLIT_REGEX`, removing every word <=
    :any:`config.MIN_WORD_LENGTH`.

    Example:
        >>> utils.tokenize('hello there, how are you')
        ['hello', 'there']

    """
    return [
        w for w in re.split(config.STR_SPLIT_REGEX, string.lower())
        if len(w) > config.MIN_WORD_LENGTH
    ]


def max_distance(sequence, idx):
    """
    Given a list an int in range(len(sequence)), determine the maximum
    amount of `movements` available from that index position in the list.

    Arguments:
        sequence (any with __len__): iterable to calculate the maximum moves
            into. It's used only to get its `len`, so any object that
            implements the `__len__` method will do.
        idx (int): index to count from.
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
