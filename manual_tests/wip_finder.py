"""
this works with the prints added in core.SearchEngine.search
that outputs final match probability and rating...
Match probability are too consistent throught all the search iterations
such as 'sherlock holmes' on 'given' returns 1.00 match (???)

As of now `search` calls for the lazy_matcher, so there might be something
there worth checking.

Usage:
------

python interpreter, copy-paste, enjoy debugging

.. TODO::
    When done remove the print statements in core.SearchEngine
"""

from search import SearchEngine
from tests.helpers import Item
[
    (setattr(i, 'category', 'books'),
     setattr(i, 'author', 'Sherlock Holmes'))
    for i in Item.setup()
]
finder = SearchEngine(['words', 'category', 'author'], limit=20)
res = finder('Sherlock', Item.items)
