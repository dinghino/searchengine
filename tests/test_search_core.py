"""
Testing module for the search core functionalities
"""
from search import core
from tests.helpers import Phrase


class TestCore:
    @classmethod
    def setup_class(cls):
        Phrase.setup()
        cls.searchPhrase = core.SearchEngine(['words'], limit=10)

    def test_single_words(self):
        seq = Phrase.get_by_length(max_length=1)

        res = self.searchPhrase('inconvene', seq)
        assert res == ['inconvenience']

        res = self.searchPhrase('laugh', seq)
        assert res == ['laughter']

    def test_short_phrases(self):
        seq = Phrase.get_by_length(3, 7)
        results = self.searchPhrase('sherlock holmes', seq)
        reversed_query_results = self.searchPhrase('holmes sherlock', seq)

        expected = [
            'Sherlock Holmes upon the grey walls.',
            'You have heard of you, Mr. Holmes.',
            'I went home with you.'
        ]

        assert results == expected
        assert reversed_query_results == expected
        results = self.searchPhrase('watson', seq)
        assert results == ['Ah, Watson, you have learned something!', ]

    def test_search_with_params(self):
        seq = Phrase.get_by_length(7, 10)
        res = self.searchPhrase('sherlock holmes', seq, limit=2, threshold=.95)
        expected = [
            'About nine o\'clock Sherlock Holmes had not yet returned.',
            'Oh, Mr. Holmes, my hair to the bitter end.',
            # 'Sherlock Holmes and I wrote to the old English capital.'
        ]
        assert res == expected

    def test_search_long_phrases(self):
        seq = Phrase.get_by_length(7, 20)
        results = self.searchPhrase('sherlock holmes', seq)
        expected = [
            'About nine o\'clock Sherlock Holmes had not yet returned.',  # noqa: E501
            'Holmes gazed long and complex story was so remarkable in its details that it may be set aside altogether.',  # noqa: E501
            'Holmes thrust his long arm to turn my face away from each other.',  # noqa: E501
            'Oh, Mr. Holmes, my hair to the bitter end.',  # noqa: E501
            'Sherlock Holmes and I find that I am a widower and never would look at a wayside public-house.',  # noqa: E501
            'Sherlock Holmes and I wrote to the old English capital.',  # noqa: E501
            'Sherlock Holmes clapped his hands together in a dark silhouette against the wall at the lock.',  # noqa: E501
            'Sherlock Holmes clapped the hat upon his knee.',  # noqa: E501
            'Sherlock Holmes closed his eyes travelled round and round the edge.',  # noqa: E501
            'Sherlock Holmes had brought a gush of hope which sank into a desultory chat with me over in despair.',  # noqa: E501
        ]
        assert results == expected
