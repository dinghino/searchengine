"""
Matcher functions to determine similarity between two strings

Using different algorithms and given two strings, each function returns a
value between 0 and 1, where 0 is completely different and 1 represent complete
equality (as in "hello world", "hello world")
"""
from search import utils, config


# =====================================================================
# String similarity functions
# ---------------------------------------------------------------------
# A set of functions that calculate the edit distance between two
# strings

def simple_ratio(query, string):
    return utils.ratio(query, string)


def best_token_ratio(query, string):
    query = utils.sorted_unique_tokens(query)
    string = utils.sorted_unique_tokens(string)
    string = utils.stringify_tokens(string)

    prob = 0
    for segment in query:
        match = utils.best_partial_ratio(segment, string)
        prob = match if match > prob else prob
        if prob == 1:
            break
    return prob


def token_sort_ratio(query, string):
    """
    generate tokens from query and string, then for each query token
    find the best partial ratio on the string and get the average value
    """
    query_tokens = utils.sorted_unique_tokens(query)
    string_tokens = utils.sorted_unique_tokens(string)
    # generate and sort a set of strings, removing duplicates, then
    # join them together again as they are (no spaces or punctuation)
    tokenized_string = utils.stringify_tokens(string_tokens)

    matches = {}
    for q_token in query_tokens:
        # loop every token in the query, adding a default similarity == 0
        # to the matches dictionary
        matches[q_token] = 0
        # loop for every word in the searched string
        for token in utils.shifter(tokenized_string, len(q_token)):
            # and call the slider on each of them, getting the similariy
            # for every extracted token
            match = utils.ratio(q_token, token)
            if match > matches[q_token]:
                matches[q_token] = match
                # FIXME: Using average this shouldn't be here!
                # if match == 1:
                #     break

    return utils.average(matches.values())


def intersect_token_ratio(query, string):
    """
    Perform a match utilizing the intersection method.
    """
    query = utils.sorted_unique_tokens(query)
    string = utils.sorted_unique_tokens(string)
    common, diff_q, diff_s = utils.sorted_intersect(query, string)
    t0 = ''.join(common)            # common elements for query and string
    t1 = ''.join(common + diff_q)   # common plus the diff elements on query
    t2 = ''.join(common + diff_s)   # common plus diff elements on string
    best = 0
    for (q, s) in ((t0, t1), (t1, t2), (t0, t2)):
        match = utils.ratio(q, s)
        if match > best:
            best = match
            if best == 1:
                break

    return best

# =====================================================================
# Full matchers functions
# ---------------------------------------------------------------------
# A set of functions that perform various checks and matches agains
# a query and a string and return a comprehensive value representing
# the equality of the two strings


def lazy_match(query, string):

    query_tokens = utils.tokenize_set(query)
    string_tokens = utils.tokenize_set(string)
    shortest, longest = sorted((query_tokens, string_tokens))
    len_short, len_long = len(shortest), len(longest)

    # If the longest has no length it's useless to continue
    if len_long == 0:
        return 0

    if len_long == 1:
        # len_short == 1 too, so 1 word against 1 word
        return simple_ratio(query, string)
    if len_short == 1 and len_long < 4:
        # at most one word against a short string
        return best_token_ratio(query, string)

    if len_short < 3 and len_long < 5:
        # if the length of the short is enough, try with a
        return token_sort_ratio(query, string)

    else:
        # in any other condition, such as short query against long string
        # use intersect_ratio
        return intersect_token_ratio(query, string)


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
    max_moves = utils.max_distance(long_, word_index=long_idx)

    return abs(1 - (moves / max_moves))
