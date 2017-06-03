# SearchEngine

A generic search engine for lists of objects,
made as a prototype for another project i'm working on, in collaboration.

## Basic usage

```python
from search import search

# Have some objects ready to search!
class Item:
    def __init__(self, v):
        self.value = v

names = ['john doe', ]  # some data
collection = [Item(name) for name in names]

result = search('john', ['value'], collection)

```

## Building documentation

from the `docs` folder run `make html` to manually build the documentation with sphinx.

For development purposes

    sphinx-autobuild ./source _build_html

can be used to hot reload the documentation that will be served at `127.0.0.1:8000`.

## Testing

_coming soon_ with pytest

## License

Released under [MIT License](/LICENSE)