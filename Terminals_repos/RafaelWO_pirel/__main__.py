# proj_clean/pirel/__main__.py

import click
from .cli import main, list_releases, check_release, ask_random_question, version_callback, logging_callback
from ._cache import clear
from ._guess import store_question_score
from .logging import setup_logging

@click.group()
@click.option('--verbose', count=True, help="Increase verbosity.")
@click.option('--version', is_flag=True, callback=version_callback, expose_value=False, is_eager=True, help="Show the version and exit.")
@click.option('--no-cache', is_flag=True, help="Disable caching.")
@click.pass_context
def cli(ctx, verbose, no_cache):
    ctx.ensure_object(dict)
    ctx.obj['VERBOSE'] = verbose
    ctx.obj['NO_CACHE'] = no_cache
    setup_logging(verbose)

cli.add_command(main)
cli.add_command(list_releases)
cli.add_command(check_release)
cli.add_command(ask_random_question)
cli.add_command(clear)

if __name__ == "__main__":
    cli()