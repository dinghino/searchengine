import click
from tests.helpers import Item, PHRASES
from search import search
# create the items
[Item(p) for p in PHRASES]


def main():
    while True:
        click.clear()

        query = click.prompt('Search')
        if query == '*':
            break

        results = search(query, ['words'], Item.items, limit=20)
        for i, item in enumerate(results):
            print('{:0>3}.  {}'.format(i + 1, item.words))

        click.pause()


if __name__ == '__main__':
    main()
