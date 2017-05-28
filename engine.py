import logging
import re

import click
import jellyfish

from test_data import people  # noqa - testing purposes, not used here

# matching treshold to consider a search result a probable match
THRESHOLD = 0.75

log = logging.getLogger('SearchEngine')


class Match:
    """
    A Match object takes care of calculating and represents
    the chance that item matches the search query, given a dataset of
    distances from the query and a set of item attributes.
    """

    def __init__(self, query, item, threshold):
        self.query = query
        # TODO: Remove the item when it's not needed anymore for developing
        # purposes. remember to remove it from the __repr__ call too.
        self.item = item
        self.threshold = threshold

        # organized data structure with all the relevant data from all the
        # `add`ed match dictionaries, that will be used to calculate the
        # item's match probability against the object
        self._matches = {}
        # self._matches = {
        #     <match.key>: {
        #         'match': <float>  <- avg mean on highest queries matches
        #         <match.weight>: <int>,
        #         'queries': {
        #             <match.query>: [<float>, ...]
        #         }
        #     }
        # }
        # actual match weight, weighted mean for all the matches
        self.weight = 0
        # highest match value currently present in _matches
        self.match = 0
        # highest matching key
        self.key = ''

    def add(self, match):
        k, w = match['key'], match['weight']
        q, m = match['value'], match['match']

        keydata = self._matches.setdefault(k, {'weight': w, 'queries': {}})
        querydata = keydata['queries'].setdefault(q, [])
        querydata.append(m)

        self._log_match_dict(match)

    def _log_match_dict(self, match):
        # NOTE: LOGGING STUFF
        good = match['match'] >= .75
        mstring = 'NEW MATCH DICT: [ m: {m:.2f} - w: {w:.2f} ] ({q}) {k}: {v}'
        mstring = mstring.format(
            q=match['query'],
            k=match['key'],
            v=match['value'],
            m=match['match'],
            w=match['weight']
        )
        string = click.style('{}'.format(mstring),
                             fg='yellow' if good else 'blue')

        log.debug(string)

    # def _get_primary_match(self):
    #     """Return the match dict with the highest match value. """
    #     m = None
    #     for m in self._matches

    def calculate(self):
        """
        Calculate the match with all the data added.
        This method should be called when all the dataset have been added
        to the match object.
        """
        d = self._matches
        log.debug('Calculated match results:')
        total_weight = 0
        total_match = 0

        for k in d.keys():
            # get the highest match for each query/attr set, then calculate
            # the match for the key as a mean avg from all the highest
            # values
            weight = d[k]['weight']
            queries = d[k]['queries']

            # sorted high->low of all the highest matches on each query
            h_match = sorted([max(qmatch) for qmatch in queries.values()])
            # factor in the `weight` of each match, using its position in
            # the list as weight. this means that highest values have
            # highest weight.
            h_match = [m * (w + 1) for w, m in enumerate(h_match)]
            # weighted average
            match = sum(h_match) / sum(range(1, len(h_match) + 1))

            d[k]['match'] = match

            # add the key weight to the total weight
            total_weight += weight
            total_match += (match * weight)

            # if the currently evaluated match is higher that the
            # `primary match value`, switch both match and key
            if match > self.match:
                self.match = match
                self.key = k

            # NOTE: Logging stuff
            ms = ''.join(['{:.2f}, '.format(m) for m in h_match])[:-2]
            log.debug(click.style(
                '  {}: {:.2f} [{}]'.format(k, match, ms),
                fg='yellow' if match >= self.threshold else '')
            )

        # average weigthed mean between the matches and the key weights
        # produces the actual weight of the match, that can be used
        # in a Result to position it in its rightful place.
        self.weight = (total_match / total_weight) + self.match

    @property
    def is_valid(self):
        return self.match >= self.threshold

    def __repr__(self):
        return '<Match ({q} @ {i}) W: {w:.3f} V: {v:.3f}>'.format(
            q=self.query,
            i=self.item,
            w=self.weight,
            v=self.match)


class Result:
    def __init__(self, data, match):
        """Result generated through a search.

        Args:
            data (any): search result object
            match (:class:`Match`): Match object describing
                similarity between the `data` and the search query
        """

        self.data = data
        self.match = match

    def __repr__(self):
        return '<Result ({v:<3.2f}% | {w:.2f}) on "{k}" [ {d} ]>'.format(
            d=self.data,
            k=self.match.key,
            v=self.match.match * 100,
            w=self.weight,
        )

    @property
    def weight(self):
        return self.match.weight

    def __lt__(self, other):
        return self.weight < other.weight


class SearchEngine:

    def __init__(self, keys, limit=-1, threshold=THRESHOLD):
        self.threshold = threshold
        self.limit = limit

        self.results = []
        # Weight for all the keys passed, from 1 to the number of keys.
        # weight is in reverse order, meaning that first keys weights more
        key_values = reversed(range(1, len(keys) + 1))
        self.keys = dict(zip(keys, key_values))

    def _jaro_winkler(self, s1, s2):
        return jellyfish.jaro_winkler(s1, s2, long_tolerance=True)

    def _damerau_levenshtein(self, s1, s2):
        # TODO: Make it return a [0-1] value (1 more similar) instead of the
        # distance value
        return jellyfish.damerau_levenshtein_distance(s1, s2)

    def get_distance(self, s1, s2, algo='jaro winkler'):
        """
        Return the distance between s1 and s2, using one of the algorithms
        allowed.
        """
        algos = {
            'jaro winkler': self._jaro_winkler,
            'damerau levenshtein': self._damerau_levenshtein,
        }
        try:
            distance_func = algos[algo]
            # TODO: normalize the strings removing non [a-zA-Z0-9] characters
            return distance_func(s1.lower(), s2.lower())

        except KeyError as e:
            raise KeyError(
                'Search algorithm should be one of {}'.format(algos.keys())
            )

    def get_match(self, query, item, keys=None):
        """
        Calculate the equality match between `query` and `item`, checking
        all the item's `keys` provided when the search engine was setup.

        Returns:
            dict: contains the `key`, `value` and key `weight` of the highest
                match found

                .. code-block:: python

                    match = {
                        'key': 'fname',
                        'value': 0.847923232323,
                        'weight: 2
                    }

        """
        match = Match(query, item, self.threshold)
        keys = keys or self.keys

        def splitter(string):
            return re.split(r'\W+', string)

        q_strings = splitter(query)

        for key, weight in keys.items():
            attr = getattr(item, key, None)
            if not attr:
                # TODO: Maybe raise exception, since at least one of the
                # given keys are not present in the object?
                continue

            for partial in splitter(attr):
                if len(partial) <= 3:  # skip short words
                    continue
                for q in q_strings:
                    match_dict = {
                        'key': key,
                        'value': partial,
                        'query': q,
                        'weight': weight,
                        'match': self.get_distance(q, partial),
                    }
                    match.add(match_dict)

        match.calculate()

        # NOTE: Logging stuff
        string = click.style(
            str(match),
            fg='green' if match.is_valid else '',
            bold=True if match.is_valid else False,
        )
        log.info(string)
        log.info('{}\n'.format('-' * 79))

        return match

    def search(self, query, items, limit=None, keys=None):
        self.results = []
        # Get the distance from the query for all the items in the items seq
        # matches = [self._jaro_winkler(query, item) for item in items]
        matches = [self.get_match(query, item, keys) for item in items]

        # Generate the Results list if the match is high enough
        self.results = [
            Result(i, m) for i, m in
            zip(items, matches) if m.is_valid
        ]

        # sort by match and return the results
        self.sort_results_by_match()
        limit = limit or self.limit
        results = self.results[:limit] if limit > 0 else self.results
        # TODO: optional extra sorting of extracted results, i.e. by attribute
        return results

    def sort_results_by_match(self):
        self.results.sort(reverse=True)

    def __call__(self, query, items):
        """
        Allow to call the engine directly to perform a search.
        """
        return self.search(query, items)
