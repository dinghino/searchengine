"""
Testing module for the search core functionalities
"""
from search import core
from tests.helpers import Item


class TestCore:
    @classmethod
    def setup_class(cls):
        cls.items = Item.setup()
        cls.search = core.SearchEngine(['words'], limit=10)

    def test_single_words(self):
        seq = Item.get_by_length(max_length=1)

        res = self.search('inconvene', seq)
        assert res == ['inconvenience']

        res = self.search('laugh', seq)
        assert res == ['laughter']

    def test_short_phrases(self):
        seq = Item.get_by_length(3, 5)
        results = self.search('sherlock holmes', seq)
        reversed_query_results = self.search('holmes sherlock', seq)
        expected = [
            'sherlock holmes clapped upon knee',
            'sherlock holmes foretold exquisite mouth',
            'sherlock holmes upon grey walls',
            'sherlock holmes wrote english capital',
        ]

        assert results == expected
        assert reversed_query_results == expected
        results = self.search('watson', seq)
        assert results == [
            "watson have learned something",
            "what wanted what doctor watson",
        ]

    def test_search_with_params(self):
        seq = Item.get_by_length(3, 5)
        res = self.search('sherlock holmes', seq, limit=2, threshold=.95)
        expected = [
            'sherlock holmes clapped upon knee',
            'sherlock holmes foretold exquisite mouth',
        ]
        assert res == expected

    def test_search_long_phrases(self):
        seq = Item.get_by_length(12, 15)
        results = self.search('sherlock holmes', seq)
        expected = [
            'facts these about four clock when sherlock holmes took step between wharf ruffian pursued',            # noqa: E501
            'moment intimacy there were other traces sherlock holmes stopped front aberdeen shipping company',      # noqa: E501
            'rushed down just have taken mind understand from some small dealings with sherlock holmes',            # noqa: E501
            'sherlock holmes brought gush hope which sank into desultory chat with over despair',                   # noqa: E501
            'sherlock holmes great many scattered papers have whatever bears upon stone professional work attend'   # noqa: E501
        ]
        assert results == expected
