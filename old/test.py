import jellyfish as jf
from utils import clean_split, pos_dist, _dec
# from test_data import profiles


def calculate(query, string):
    # split the two strings cleaning out some stuff
    query = clean_split(query.lower())
    string = clean_split(string.lower())
    print('Q: {} | S: {}'.format(query, string))
    # sort the two generated lists and set them in position
    shortest, longest = sorted((query, string), key=lambda x: len(x))

    # both currently used for debugging on commented print statements
    len_shortest = len(shortest)  # noqa
    len_longest = len(longest)    # noqa

    # matrix of tuples for each segment of both query and string
    matrix = [(s1, s2) for s1 in longest for s2 in shortest]

    matches = {}
    for s1, s2 in matrix:
        # get the jaro winkler equality between the two strings
        m = jf.jaro_winkler(s1, s2, long_tolerance=True)
        # calculate the distance factor for the position of the segments
        # on their respective lists
        d = pos_dist(s1, s2, longest, shortest)

        # get them together and append to the matches dictionary
        match = (m, d)
        print('- {} -> {} | M:{}, D:{}'.format(s1, s2, _dec(m), _dec(d)))
        matches.setdefault(s1, []).append(match)

        # =====================================================================
        # Segments with ratio >= treshold found
        # =====================================================================
        # TODO: Add a ratio for matching?
        # TODO: factor in how many query segments have been found in string.
        # more segments found means that what has been found is more coherent
        # with the string value

        # =====================================================================
        # Relative distance for segments
        # =====================================================================
        # TODO: Somewhere (here or in utils.pos_dist) there is a need to factor
        # in the RELATIVE distance between the found segments, meaning that if
        # two OK segments have a positional distance == 1 on the query
        # and the string they weight more that if they were more apart.
        # Logically this means that you searched for 'set of chair' and an item
        # named 'table with set of chairs' has more chance to be what you were
        # looking for instead of "set of tables with chair".

    # get the highest value for each list, the apply the word-distance factor
    matches = [max(m, key=lambda x: x[0]) for m in matches.values()]
    matches = [(m + d) / 2 for m, d in matches]

    # get the weighted mean for all the highest matches and apply the
    # segments qty diff as coefficient, to consider the
    # missing/extra values on one of the lists
    # ================================================
    # * (len_shortest / len_longest) => should be added at the end once the
    # ------------------------------------------------
    # TODO that requires to consider the nearby words as more important is in
    # place. the ratio represent the lenght difference of the two strings,
    # meaning that you may have searched for something similar (
    # 'garden chair', 'kitchen chair') instead of something more (or less)
    # descriptive ('modern style kitchen chair'). This allows to have more
    # similar results in both distance value and length value first
    mean_match = (sum(matches) / len(matches))
    return mean_match, max(matches)


results = []


def execute(query, string):
    global results
    # print('QUERY: {} | STRING: {}'.format(query, string))
    prob, high = calculate(query, string)
    results.append({
        'q': query,
        's': string,
        'prob': prob,
        'high': high
    })
    print('{}%, highest: {}'.format(_dec(prob * 100), _dec(high)))
    print('-' * 79)
    print()


# dataset = [p.name for p in profiles]
dataset = [
    'sedia',
    'sedia semplice',
    'set di sedie da giardino',
    'sedie da salotto',
    'sedia deco',
    'sedia a sei zampe',
    'tavolo con set di sedie',
    'sgabello da cucina',
    'set da quattro sedie',
    'set da sei sedie',
    'set da dodici sedie',
]
# execute('ciao come stai', 'ciao come stai')
# execute('ciao come stai', 'stai come ciao come')
# execute('ciao come', 'ciao come stai')
# execute('ciao come stai', 'ciao come')
# execute('ciao come stai', 'andiamo a como vero')
# execute('ciao come stai', 'a comodo')
# execute('pinco', 'pinco pallo')
# execute('pinco pallo', 'pinco pallo')
# execute('pallo pinco', 'pinco pallo')
# execute('ballo', 'pinco qwey')

for n in dataset:
    execute('set di sedie', n)

results.sort(key=lambda o: o['prob'])
for r in results:
    print(
        'Q: {q} | S: {s}\nProb: {p:.2f}%\n{d}'.format(
            q=r['q'], s=r['s'], p=r['prob'] * 100, d='-' * 79)
    )
