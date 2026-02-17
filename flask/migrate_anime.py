import json
import os
from app import app, db
from app.models.anime import Anime, Genre, anime_genres
from app.models.authuser import AuthUser


def do_migrate_anime():
    path = os.path.join(app.root_path, "data", "anime_list.json")
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        anime_list = json.load(f)

    # Fetch all users
    users = AuthUser.query.all()
    if not users:
        print("Warning: No users found in DB. Skipping migration.")
        return

    print("Clearing existing anime records for a fresh migration...")
    # Clear association table first to avoid FK violations
    db.session.execute(anime_genres.delete())
    Anime.query.delete()  # Clear all to start round-robin from scratch
    db.session.commit()

    print(
        f"Distributing {len(anime_list)} anime among {len(users)} "
        "users in round-robin fashion."
    )

    for i, item in enumerate(anime_list):
        user = users[i % len(users)]
        mal_id = item.get("mal_id")
        if not mal_id:
            continue

        # In round-robin with unique items, we don't strictly need to check
        # for existence but it's good practice. Since we just deleted all,
        # this is safe.

        print(
            f"Migrating {item.get('title_english') or item.get('title')} "
            f"for {user.username} (Index: {i})..."
        )
        anime = Anime(
            mal_id=mal_id,
            title_english=item.get("title_english") or item.get("title"),
            image_url=item.get("image_url"),
            year=(item.get("year") if item.get("year") != "N/A" else None),
            episodes=(
                item.get("episodes") if item.get("episodes") != "N/A" else None
            ),
            synopsis=item.get("synopsis"),
            score=(item.get("score") if item.get("score") != "N/A" else 0.0),
            owner_id=user.id,
            my_rating=item.get("my_rating") or 0,
            deleted_at=None,
        )
        # Add to session first to avoid SAWarning when appending relationships
        db.session.add(anime)

        # Handle genres
        genres = item.get("genres", [])
        for g_name in genres:
            if not g_name:
                continue
            genre = Genre.query.filter_by(name=g_name).first()
            if not genre:
                genre = Genre(name=g_name)
                db.session.add(genre)
            if genre not in anime.genres:
                anime.genres.append(genre)

    db.session.commit()
    print("Migration complete!")


if __name__ == "__main__":
    with app.app_context():
        do_migrate_anime()
