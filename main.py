import click

from engine import SearchEngine
from test_data import people, profiles  # noqa
import logging

logging.basicConfig(
    format='%(levelname)-8s - %(message)s', level=logging.DEBUG
)
log = logging.getLogger('SearchEngine')
levels = {
    1: logging.ERROR,
    2: logging.WARNING,
    3: logging.INFO,
    4: logging.DEBUG,
}

DATASET = people


@click.command()
@click.option('-v', '--verbose', count=True, default=1,
              help='Level of verbosity, more v more verbose')
@click.option('-l', '--limit', default=-1, help='limit the number of results')
def main(verbose, limit):
    if verbose > 4:
        verbose = 4
    log.setLevel(levels[verbose])

    people_search = SearchEngine(
        keys=['fname', 'lname', 'job'],
        limit=limit,
    )
    profiles_search = SearchEngine(
        keys=['name', 'username', 'mail', 'job'],
        limit=limit,
    )

    _fnc = {
        'people': (people_search, people),
        'profiles': (profiles_search, profiles)
    }

    def search(query, where='people'):
        func, dataset = _fnc[where]
        return func(query=query, items=dataset)

    def fmt_help(first, string):
        return '{}{}'.format(
            click.style(first, bold=True),
            string
        )

    help_ = '{}\n{}\n'.format(
        fmt_help('Q', 'uit'), fmt_help('S', 'witch data'))
    search_in = 'people'

    while True:
        click.clear()
        click.echo('Searching in: {}'.format(
            click.style(search_in, bold=True)))
        click.echo(help_)
        query = click.prompt(click.style('Search', fg='green'))
        if query == 'q':
            break
        if query == 's':
            search_in = 'profiles' if search_in == 'people' else 'people'
            continue

        result = search(query, search_in)

        click.secho('\n{}'.format('-' * 79) * 3, fg='yellow')

        click.secho('Found {} results for "{}"'.format(
            len(result), query), bold=True)

        for i, r in enumerate(result):
            click.echo('[{:0>3d}] - {}'.format(i + 1, r))

        click.pause()


if __name__ == '__main__':
    main()
