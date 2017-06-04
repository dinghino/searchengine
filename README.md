# PyFinder
_Yet another search engine built in python_.

This project contains a really simple search engine capable of digesting any list of objects of any kind, made as a prototype for another project i'm working on, in collaboration with [@simo86](https://github.com/simo86).
Since I liked where it was going, we extracted it from the main project to improve it and make it standalone.

## Why?

There are lots and lots of search engines in python. This is another one, made expressly for prototyping and for placeholding. allows simple queries on any type of objects - as long as you search on strings attributes - and works directly on iterable of such objects (coming from any source, like _list_ or even _generator_ functions).

For this reason it's probably not well suited to work in production, but for testing purposes should do its job.

Also, since it does not rely on any kind of stored index - either in file or in a database - can work everywhere your python application can run.



## Basic usage

```python
from search import SearchEngine

# Have some objects ready to search!
class Item:
    def __init__(self, v):
        self.value = v

names = ['john doe', ]  # some data
collection = [Item(name) for name in names]

engine = SearchEngine(['value'], limit=10)

result = engine.search('john', collection)
# or directly engine('john', collectio)

```

## Documentation

built documentation can be found on [read the docs](http://pyfinder.readthedocs.io/en/latest/).

To locally build your documentation go inside the `docs` folder and run `make html` to build it with sphinx.

For development purposes

    sphinx-autobuild ./source _build_html

can be used to hot reload the documentation that will be served at `127.0.0.1:8000`.

## Testing

Tests are built with `pytest`, so to quickly run tests:

    pytest

More options can be found in [pytest documentation](https://docs.pytest.org/en/latest/contents.html)

## License

Released under [MIT License](/LICENSE)