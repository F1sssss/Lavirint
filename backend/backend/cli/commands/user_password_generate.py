import click
from passlib.handlers.pbkdf2 import pbkdf2_sha256


@click.command(name='user:password:generate')
@click.option('-p', '--password', prompt=True, hide_input=True, confirmation_prompt=True)
def user_password_generate(password):
    click.echo(pbkdf2_sha256.hash(password))
