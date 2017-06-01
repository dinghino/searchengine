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

## Testing

_coming soon_ with pytest

## License

Released under [MIT License](/LICENSE)