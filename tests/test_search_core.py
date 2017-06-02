"""
Testing module for the search core functionalities
"""
from search import core
from tests.helpers import Item, PHRASES


# TODO: Delete. used for pdb sequences of Item
def ps(seq):
    [print(v) for v in seq]


class TestCore:
    @classmethod
    def setup_class(cls):
        [Item(words) for words in PHRASES]
        cls.items = Item.items

        def search(cls, query, sequence):
            return core.search(query, ['words'], sequence, limit=10)
        cls.search = search

    def test_single_words(self):
        seq = Item.get_by_length(max_length=1)

        res = self.search('inco', seq)
        assert res == ['inconvenience']

        res = self.search('laug', seq)
        assert res == ['laughter']

    def test_short_phrases(self):
        seq = Item.get_by_length(3, 5)
        res = self.search('sherlock holmes', seq)
        res_inverted = self.search('holmes sherlock', seq)
        expected = [
            'sherlock holmes wrote english capital',
            'sherlock holmes clapped upon knee',
            'sherlock holmes upon grey walls',
            'sherlock holmes foretold exquisite mouth',
            'home with nerves worked',      # ?
        ]

        assert res == expected
        assert res_inverted == expected
        res = self.search('watson', seq)
        assert res == [
            "what wanted what doctor watson",
            "watson have learned something",
        ]
