from collections import defaultdict
import re
import jellyfish as jf

calls = 0


def splitter(string):
    return re.split(r'\W+', string)


def calculate(query, string, expected):
    global calls
    calls += 1
    print('-- [ {} ] -> {}'.format(calls, expected))
    print('-- QUERY: {} | STRING: {}'.format(query, string))

    # split the two strings cleaning out some stuff
    query = splitter(query)
    string = splitter(string)
    # sort the two generated lists, longest first
    longest, shortest = sorted([query, string])
    # similary of length (0-1)
    l_similar = len(longest) / len(shortest)
    # generate a matrix of tuples for each segment of both query and string
    matrix = [
        (s1, s2) for s1 in longest for s2 in shortest
        if len(s1) >= 3 and len(s2) >= 3
    ]

    # calculate the similarity (distance) for each tuple of the matrix
    # and group them by the longest string's segments. this allows us
    # to be sure to have checked all the combinations
    matches = defaultdict(list)
    [matches[s1].append(jf.jaro_winkler(s1, s2)) for s1, s2 in matrix]

    # get the highest value for each list
    matches = [max(matches[k]) for k in matches]
    # get the weighted mean for all the highest matches and apply the
    # lenght distance as coefficient, to consider the missing/extra values
    # on one of the lists
    return (sum(matches) / len(matches)) * l_similar


print('{:.2f}%'.format(calculate('ciao come stai', 'ciao come stai', '100%') * 100))
print()
print('{:.2f}%'.format(calculate('ciao come stai', 'stai come ciao come', '100%') * 100))
print()
print('{:.2f}%'.format(calculate('ciao come', 'ciao come stai', '83.4%') * 100))
print()
print('{:.2f}%'.format(calculate('ciao come stai', 'ciao come', '83.4%') * 100))
print()
print('{:.2f}%'.format(calculate('ciao come stai', 'andiamo a como vero', '~ 70%') * 100))
print()
print('{:.2f}%'.format(calculate('ciao come stai', 'a comodo', '< 50%') * 100))
print()
