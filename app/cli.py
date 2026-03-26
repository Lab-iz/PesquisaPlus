import click

from .extensions import db
from .services.seed_service import seed_database


def register_commands(app):
    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        click.echo("Banco inicializado com sucesso.")

    @app.cli.command("seed")
    def seed():
        db.create_all()
        seed_database()
        click.echo("Dados de exemplo carregados.")

    @app.cli.command("reset-db")
    def reset_db():
        db.drop_all()
        db.create_all()
        seed_database(force=True)
        click.echo("Banco recriado com seed completa.")
