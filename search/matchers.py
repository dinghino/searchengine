
import jellyfish
from search import utils, config


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
        match = jellyfish.jaro_winkler(string1, string2)
        # calculate the distance factor for the position of the segments
        # on their respective lists
        positional = utils.position_similarity(string1, string2, long_, short)

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
