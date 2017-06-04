from search.core import SearchEngine  # noqa: F401
"""
Fuzzy Search engine
=====================

.. contents:: :local:

Introduction
------------

This package contains a simple search engine to crawl any collection of objects
and return matching values. Uses no database or storage, of any sort, requires
little to no so setup, so it can be used everywhere in no time.

Anyway it can be used to digest any type of object-like collection, as long
as ``getattr(object, '<attribute>')`` returns a value, so for quick search
implementation on small dataset, as placeholder, prototyping or for testing
purposes it does the trick.

As of now it works only on strings, so no numeric values (as in `int` or
`float`), `datetime` etcetera can be used to match and sort the items.

.. note::
    This is a simple search algorithm that implements just a few checks
    and while it tries to do a full text search in an efficient way, as of now
    it cannot be relied upon with the utmost certainty.


Basic usage
-----------

.. code-block:: python

    from search import SearchEngine

    collection = Model.select()  # returns an iterable of objects
    search_engine = SearchEngine(['attr_name'], limit=10)
    results = search_engine.search('query', collection)
    # [...]

    results = search_engine.search('query', collection, limit=-1)
    # [all items over equality threshold]

    results = search_engine('query', collection)
    # callable object, since we are lazy



Algorithm
---------

Basic search functionality tries to do a `sort-of` full text search that relies
on the `Jaro-Winkler <https://goo.gl/b59g4v>`_ algorithm to calculate the
distance between words in a matrix `query * term`, the `movement cost` for each
word in the phrases (words not where they should be have less value) and on a
weigth value when searching through multiple model attributes.

Since I'm no mathematician I can't actually put down a formula for you, sorry.
Feel free to check the code and come up with something :)


Tweaking
--------

Basic algorithm configuration can be found in :any:`search.config`, that allows
some tweaking on how it filters words and weights stuff.
"""
