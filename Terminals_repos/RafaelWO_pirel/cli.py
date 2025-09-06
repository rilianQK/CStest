# proj_clean/pirel/cli.py

import click
import logging
from . import CONTEXT
from ._cache import clear
from ._guess import get_random_question, store_question_score
from .python_cli import get_active_python_info
from .releases import load_releases, PythonReleases
from .logging import setup_logging

logger = logging.getLogger(__name__)

@click.command()
@click.pass_context
def main(ctx):
    """The Python release cycle in your terminal."""
    if ctx.obj['NO_CACHE']:
        releases = load_releases()
    else:
        cache_file = get_latest_cache_file()
        if cache_file and calc_cache_age_days(cache_file) <= 7:
            releases = PythonReleases(load(cache_file))
        else:
            releases = load_releases()
            save(releases.to_dict())
    CONTEXT.releases = releases
    print_releases()

@click.command()
@click.pass_context
def list_releases(ctx):
    """Lists all Python releases in a table. Your active Python interpreter is highlighted."""
    releases = CONTEXT.releases
    active_python_info = get_active_python_info()
    if active_python_info:
        active_version = active_python_info.version
    else:
        active_version = None
    table = releases.to_table(active_version)
    CONTEXT.rich_console.print(table)

@click.command()
@click.pass_context
def check_release(ctx):
    """Shows release information about your active Python interpreter."""
    active_python_info = get_active_python_info()
    if not active_python_info:
        click.echo("No active Python interpreter found.")
        ctx.exit(2)
    release = CONTEXT.releases[active_python_info.version]
    CONTEXT.rich_console.print(release)
    if release.is_eol:
        ctx.exit(1)

@click.command()
@click.pass_context
def ask_random_question(ctx):
    """Prompts the user with a random question regarding Python releases."""
    question = get_random_question()
    correct = question.ask()
    store_question_score(question, int(correct))
    if correct:
        click.echo("Correct!")
    else:
        click.echo("Incorrect.")

@click.command()
@click.pass_context
def version_callback(ctx, value):
    """Print the version of the 'pirel' package and exit the program when a boolean flag is set to True."""
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"pirel version {__version__}")
    ctx.exit()

@click.command()
@click.pass_context
def logging_callback(ctx, verbosity):
    """Configure logging verbosity based on the provided verbosity level."""
    if ctx.resilient_parsing:
        return
    setup_logging(verbosity)

def print_releases():
    """Prints all Python releases as a table."""
    releases = CONTEXT.releases
    active_python_info = get_active_python_info()
    if active_python_info:
        active_version = active_python_info.version
    else:
        active_version = None
    table = releases.to_table(active_version)
    CONTEXT.rich_console.print(table)