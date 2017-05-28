import logging

import click
import jellyfish

from test_data import people  # noqa - testing purposes, not used here

# matching treshold to consider a search result a probable match
THRESHOLD = 0.75

log = logging.getLogger('SearchEngine')


class SearchEngine:
    class Match:
        """
        A SearchEngine.Match object takes care of calculating and represents
        the chance that item matches the search query, given a dataset of
        distances from the query and a set of item attributes.
        """

        def __init__(self, query, item, threshold):
            self.query = query
            self.item = item
            self.threshold = threshold

            self._matches = []
            # actual match weight, weighted mean for all the matches
            self.weight = 0
            # highest match value currently present in _matches
            self.match = 0
            # highest matching key
            self.key = ''
            # used to calculate self.weight when a new match is added
            self._tot_weight = 0
            self._tot_match = 0

        def add(self,
                match={'key': '', 'value': '', 'match': 0.0, 'weight': 0}):

            match['weight'] = ((match['match']**2) * match['weight']) + 1

            self._matches.append(match)
            # matches with higher `match` first
            self._matches.sort(key=lambda m: m['match'], reverse=True)

            # set the new match and key attributes from the
            # match dict with the highest match
            self.match = self._matches[0]['match']
            self.key = self._matches[0]['key']

            self._update_mean_weight(match)

            # NOTE: LOGGING STUFF
            good = match['match'] >= .75
            string = click.style('{}'.format(match),
                                 fg='yellow' if good else 'blue')

            log.debug(string)

        def _update_mean_weight(self, match):
            # calculate the new weighted mean
            # FIXME: The problem is here. the weight of the
            self._tot_match += (match['match'] * match['weight'])
            self._tot_weight += match['weight']
            self.weight = self._tot_match / self._tot_weight
            # factor in the actual match distance on the weight
            self.weight *= self.match

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
                match (:class:`SearchEngine.Match`): Match object describing
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
        match = SearchEngine.Match(query, item, self.threshold)
        keys = keys or self.keys
        q_strings = query.split(' ')

        for key, weight in keys.items():
            attr = getattr(item, key, None)

            match_dict = {
                'key': key, 'value': attr,
                'weight': weight, 'match': 0,
            }
            # populated by all the distances found while looping all the
            # `attr` partial strings against all the partial query strings
            values = []
            if not attr:
                # TODO: Maybe raise exception, since at least one of the
                # given keys are not present in the object?
                continue

            for partial in attr.split(' '):
                for q in q_strings:
                    values.append(self.get_distance(
                        q, partial))

            match_dict['match'] = max(values)

            match.add(match_dict)

        # NOTE: Logging stuff
        is_match = match.weight >= self.threshold
        string = click.style(
            str(match),
            fg='green' if is_match else '',
            bold=True if is_match else False,
        )
        log.info(string)
        log.info('{}\n'.format('-' * 50))

        return match

    def search(self, query, items, limit=None, keys=None):
        self.results = []
        # Get the distance from the query for all the items in the items seq
        # matches = [self._jaro_winkler(query, item) for item in items]
        matches = [self.get_match(query, item, keys) for item in items]

        # Generate the Results list if the match is high enough
        self.results = [
            SearchEngine.Result(i, m) for i, m in
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
