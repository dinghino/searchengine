from search import utils

with open('./tests/phrases.txt') as fo:
    PHRASES = fo.read().split('\n')

# TODO: manually tokenize the phrases, then save the tokenized values
PHRASES = [utils.tokenize(phrase) for phrase in PHRASES]
PHRASES.sort(key=lambda x: len(x))


class Item:
    """
    Wrapper objects for iterable of strings (produced by a tokenizer) built
    specifically for testing purposes and matching against strings.
    """
    items = []  # quick access. may go when creating stuff

    def __init__(self, words):
        self.words = words
        self.length = len(words)
        Item.items.append(self)

    @staticmethod
    def setup(contents=PHRASES):
        Item.items = [Item(phrase) for phrase in contents]
        return Item.items

    @staticmethod
    def get_by_length(min_length=0, max_length=1):
        """
        Get an alphabetically sorted list of items that wrap a phrase with
        min_length to max_length words. if max_length equals `-1` all the items
        will be returned.
        """
        if max_length == -1:
            return Item.items
        rng = range(min_length, max_length)
        return sorted([i for i in Item.items if i.length - 1 in rng])

    def __repr__(self):
        return self.words

    def __lt__(self, other):
        return self.words < other.words

    def __eq__(self, other):  # specific override to match with strings
        return self.words == other
