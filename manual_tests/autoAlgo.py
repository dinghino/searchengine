from search import matchers, utils

BOLD = '\033[1m'
ENDC = '\033[0m'

tests_data = [
    # single words on single words
    {'q': 'ciao', 's': 'ciao'},
    {'q': 'ciao', 's': 'ciaone'},
    {'q': 'ciao', 's': 'come'},

    # # single words on multi words
    # {'q': 'ciao', 's': 'ciao come stai'},
    # {'q': 'ciao', 's': 'come stai coso'},
    # {'q': 'come', 's': 'come andiamo'},

    # # multi words on multi words
    # {'q': 'ciao come', 's': 'ciao come stai'},
    # {'q': 'ciao, come stai', 's': 'ciaone come stai'},

    # fuzzywuzzy example
    {'q': 'yankees', 's': 'new york yankees'},
    {'q': 'mets', 's': 'new york yankees'},
    {'q': 'mets', 's': 'new york mets'},
    {'q': 'nets', 's': 'new york mets'},
    {'q': 'new york', 's': 'new york yankees'},
    {'q': 'new york', 's': 'new york mets'},
    {'q': 'new york yankees', 's': 'new york yankees'},
    {'q': 'new york mets', 's': 'new york yankees'},
    {'q': 'yankees new york', 's': 'new york yankees'},
    {'q': 'yankees new york mets', 's': 'new york yankees'},
    {'q': 'mariners vs angels',
     's': 'los angels angels of anaheim at seattle mariners'},
    {'q': 'new york mets vs atlanta braves',
     's': 'atlanta braves vs new york mets'}
]


results = {}


def divider(s='-'):
    print(s * 79)


def test(func, data=tests_data):
    funcname = func.__module__ + '.' + func.__name__
    divider(' ')
    print('Testing: {}'.format(BOLD + funcname + ENDC))
    print(func.__doc__)
    divider()
    divider(' ')

    for qs in data:

        divider('.')

        query, string = qs['q'], qs['s']
        m = func(query, string)

        res = results.setdefault(query + string, [])
        res.append({'q': query, 's': string, 'r': m, 'f': funcname})

        # ============ debugging ================
        print('- {} : {}'.format(query, string))
        try:
            print('>>> {:.2f}'.format(m))
        except:
            for v in m:
                print(v)
    divider(' ')
    divider('=')

# ==================================================================
# execution time


test(utils.ratio)
test(utils.best_partial_ratio)
test(matchers.best_token_ratio)
test(matchers.token_sort_ratio)
test(matchers.intersect_token_ratio)

print()
print('Grouped by query @ string')
divider('=')

for k, res in results.items():
    print('{}{}{} @ {}'.format(BOLD, res[0]['q'], ENDC, res[0]['s']))
    for t in res:
        try:
            print('- {} : {}{:.2f}{}'.format(t['f'], BOLD, t['r'], ENDC))
        except:
            pass
    divider('-')
