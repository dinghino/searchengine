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

    search = SearchEngine(keys=['fname', 'lname', 'job'])
    # search = SearchEngine(keys=['name', 'username', 'mail', 'job'])

    while True:
        click.clear()

        q_string = '{} (q to quit)'.format(click.style('Search', fg='green'))
        query = click.prompt(q_string)
        if query == 'q':
            break

        result = search(query, DATASET)

        click.secho('\n{}'.format('-' * 79) * 3, fg='yellow')

        click.secho('Found {} results for "{}"'.format(
            len(result), query), bold=True)

        for i, r in enumerate(result):
            click.echo('[{:0>3d}] - {}'.format(i + 1, r))

        click.pause()


if __name__ == '__main__':
    main()
