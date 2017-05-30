import jellyfish as jf
from utils import clean_split, pos_dist, _dec


def calculate(query, string):
    # split the two strings cleaning out some stuff
    query = clean_split(query)
    string = clean_split(string)
    # print('Q: {}\nS: {}'.format(query, string))
    # sort the two generated lists and set them in position
    shortest, longest = sorted((query, string), key=lambda x: len(x))

    len_shortest = len(shortest)
    len_longest = len(longest)

    # matrix of tuples for each segment of both query and string
    matrix = [(s1, s2) for s1 in longest for s2 in shortest]

    matches = {}
    for s1, s2 in matrix:
        # get the jaro winkler equality between the two strings
        m = jf.jaro_winkler(s1, s2)
        # calculate the distance factor for the position of the segments
        # on their respective lists
        # FIXME: Fix 0 values that kill completely the match value
        d = pos_dist(s1, s2, longest, shortest)
        # d = 1
        # get them together and append to the matches dictionary
        match = (m, d)
        # print('- {} -> {} | M:{}, D:{}'.format(s1, s2, _dec(m), _dec(d)))
        matches.setdefault(s1, []).append(match)

    # get the highest value for each list, the apply the word-distance factor
    matches = [max(m, key=lambda x: x[0]) for m in matches.values()]
    matches = [(m + d) / 2 for m, d in matches]

    # get the weighted mean for all the highest matches and apply the
    # segments qty diff as coefficient, to consider the
    # missing/extra values on one of the lists
    mean_match = (sum(matches) / len(matches)) * (len_shortest / len_longest)
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
    # print('{}%, highest: {}'.format(_dec(prob * 100), _dec(high)))
    # print('-' * 79)
    # print()


execute('ciao come stai', 'ciao come stai')
execute('ciao come stai', 'stai come ciao come')
execute('ciao come', 'ciao come stai')
execute('ciao come stai', 'ciao come')
execute('ciao come stai', 'andiamo a como vero')
execute('ciao come stai', 'a comodo')
execute('pinco', 'pinco pallo')
execute('pinco pallo', 'pinco pallo')
execute('pallo pinco', 'pinco pallo')
execute('ballo', 'pinco qwey')

results.sort(key=lambda o: o['prob'], reverse=True)
for r in results:
    print(
        'Q: {q}\nS: {s}\nProb: {p:.2f}%\n{d}'.format(
            q=r['q'], s=r['s'], p=r['prob'] * 100, d='-' * 79)
    )
