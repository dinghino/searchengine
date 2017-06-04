Yet ANOTHER search library?
============================

This project was born as an experiment and as part of a task during a class, and then continued for fun and challenge because yes.

The general idea behind this project is to have a generic search engine that can crawl through any set of objects without caring too much about setting up schemas, models, documents and indexes and regardless on what the objects actually are and have:

what it's needed is a collection of objects that have some string attributes to look into and the names of the attributes. That's it.

Since we need a collection - as in iterable - of objects, this won't have good performance when integrated with a large database or dataset (such as collections of books), as it needs to check every defined attribute for each object in the collection.

This, in other end, would do just fine for testing purposes while developing a small-to-mid sized application that may require a search engine, not currently present, and/or with models that can change signature rapidly due to development purposes.

.. note::
    I'm doing this for `fun and games`, never actually studied this stuff so I come up with how things should work as I go.
    
    At the moment there are issue when analyzing mid-long strings and/or querying with long strings longer than 1/2 words, but I'm working on it.

Installation
============

Setup your virtualenv on ``python 3.6`` with whatever tool you like, then as usual.

.. code-block:: none

    pip install -r requirements.txt

.. note::
    As of now the only real requirements for the engine to work are

    * `JellyFish <https://pypi.python.org/pypi/jellyfish>`_, used to calculate the edit distance of each segment.
    * ``pytest`` for testing.

    Jellyfish will probably go with a direct implementation of an edit distance algorithm using `difflib.SequenceMatcher` or something else,
    so, as soon as this is done, there is no need to install anything to make this work.


Basic Usage
===========

.. code-block:: python

    from search import search

    # Have some objects ready to search!
    class Person:
        def __init__(self, name):
            self.name = name

    names = ['john doe', 'mickey mouse', 'jane doe']
    collection = [Person(name) for name in names]

    result = search('john', ['name'], collection)
    # [<Person 'john doe'>]

    result = search('doe', ['name'], collection)
    # [<Person 'john doe'>, <Person 'jane doe'>]
