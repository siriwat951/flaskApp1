import json
import os
from flask.cli import FlaskGroup
from werkzeug.security import generate_password_hash
from app import app, db
from app.models.authuser import AuthUser, PrivateContact
from app.models.anime import Anime, Genre
from migrate_anime import do_migrate_anime

# from app.models.blog_entry import BlogEntry


cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.reflect()
    db.drop_all()
    db.create_all()
    db.session.commit()


@cli.command("migrate_anime")
def migrate_anime():
    do_migrate_anime()


@cli.command("seed_db")
def seed_db():
    # 1. Create Users
    if not AuthUser.query.filter_by(email="flask1@204212").first():
        user1 = AuthUser(
            email="flask1@204212",
            name="สมชาย ทรงแบด",
            password=generate_password_hash("1234", method="sha256"),
            avatar_url=(
                "https://ui-avatars.com/api/"
                "?name=สมชาย+ทรงแบด"
                "&background=83ee03&color=fff"
            ),
            # ---------------START EDIT-------------------
            username="somchai",
            # ---------------END EDIT---------------------
        )
        db.session.add(user1)
        db.session.commit()

        # Now we can add the contact using user.id
        private_contact = PrivateContact(
            firstname="ส้มโอ",
            lastname="โอเค",
            phone="081-111-1112",
            owner_id=user1.id,
        )
        db.session.add(private_contact)
        db.session.commit()

    if not AuthUser.query.filter_by(email="flask2@204212").first():
        user2 = AuthUser(
            email="flask2@204212",
            name="ส้มโอ โอเค",
            password=generate_password_hash("1234", method="sha256"),
            avatar_url=(
                "https://ui-avatars.com/api/"
                "?name=ส้มโอ+โอเค"
                "&background=83ee03&color=fff"
            ),
            # ---------------START EDIT-------------------
            username="som-o",
            # ---------------END EDIT---------------------
        )
        db.session.add(user2)
        db.session.commit()

    # 2. Migrate Anime (will use both users as owner)
    do_migrate_anime()


if __name__ == "__main__":
    cli()
