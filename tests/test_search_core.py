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

        res = self.search('inconvene', seq)
        assert res == ['inconvenience']

        res = self.search('laugh', seq)
        assert res == ['laughter']

    def test_short_phrases(self):
        seq = Item.get_by_length(3, 5)
        res = self.search('sherlock holmes', seq)
        res_inverted = self.search('holmes sherlock', seq)
        expected = [
            'sherlock holmes clapped upon knee',
            'sherlock holmes foretold exquisite mouth',
            'sherlock holmes upon grey walls',
            'sherlock holmes wrote english capital',
        ]

        assert res == expected
        assert res_inverted == expected
        res = self.search('watson', seq)
        assert res == [
            "watson have learned something",
            "what wanted what doctor watson",
        ]
