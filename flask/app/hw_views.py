# Siriwat Tidsuksai (Armmy)
# 670510727
# sec001

iimport json
import re
from datetime import datetime
from urllib.request import urlopen
from urllib.parse import quote
from flask import jsonify, render_template, request, redirect, url_for
from app import app, db, csrf
from flask_login import login_required, current_user, logout_user
from sqlalchemy import func
from app.models.anime import Anime, Genre
from app.models.authuser import AuthUser


def check_username_re(username):
    """
    Validates username format using regex.
    Rules:
    - Must start with lowercase a-z or 0-9.
    - Can only contain lowercase a-z, 0-9, _, -.
    - No spaces.
    """
    if not re.match(r"^[a-z0-9][a-z0-9_-]*$", username):
        return (
            False,
            "Must start with a-z or 0-9. Only a-z, 0-9, _, - allowed.",
        )
    return True, ""


# TASK 2: Protected Routes
@app.route("/anivault")
# TODO: Task 2 - Add @login_required
def anivault_mylist():
    return render_template("anivault/index.html", active_tab="search")


# TASK 2: Protected Routes
@app.route("/anivault/fetch")
# TODO: Task 2 - Add @login_required
def anivault_fetch():
    return render_template("anivault/fetch.html", active_tab="fetch")


# FEATURE: Public Profiles (Provided)
@app.route("/anivault/p")
def anivault_profile():
    username = request.args.get("u")
    if not username:
        return redirect(url_for("anivault_mylist"))

    # If visiting own profile, redirect to main collection page
    if current_user.is_authenticated and current_user.username == username:
        return redirect(url_for("anivault_mylist"))

    target_user = AuthUser.query.filter_by(username=username).first_or_404()
    # Check if the viewer is the logged-in user to potentially reuse index or modify it
    # We pass target_user context to the template
    return render_template(
        "anivault/index.html", active_tab="search", target_user=target_user
    )


# TASK 4: Username Validation
@app.route("/anivault/api/check_username")
@csrf.exempt
@login_required
def check_username():
    username = request.args.get("username", "").strip().lower()
    if not username:
        return jsonify({"available": False})

    is_valid, msg = check_username_re(username)
    if not is_valid:
        return jsonify({"available": False, "message": msg})

    # Check if taken by another user (case-insensitive)
    existing = AuthUser.query.filter(
        func.lower(AuthUser.username) == username
    ).first()
    is_taken = existing and existing.id != current_user.id
    return jsonify({"available": not is_taken})


# TASK 4: Username Change
@app.route("/anivault/api/update_username", methods=["POST"])
@login_required
def update_username():
    """
    Updates the user's username in the database.

    [STUDENT IMPLEMENTATION GUIDE]
    1. Get the JSON data from the request body (request.get_json()).
    2. Extract 'username', strip whitespace, and convert to lowercase.
    3. Validate that 'new_username' is not empty.
       - If empty: return jsonify({'success': False, 'message': '...'}), 400
    4. Call the helper function check_username_re(new_username) to validate format.
       - If not valid: return jsonify({'success': False, 'message': msg}), 400
    5. Check if the username is already taken by another user (case-insensitive check).
       - Query AuthUser where func.lower(AuthUser.username) == new_username.
       - If existing and existing.id != current_user.id:
         return jsonify({'success': False, 'message': 'Username already taken'}), 400
    6. If all checks pass, update current_user.username.
    7. Commit changes to the database (db.session.commit()).
    8. Return jsonify({'success': True}).
    """
    # [Task 4] Implement User Change Logic Here
    pass


# TASK 5: Filter Anime List
@app.route("/anivault/api/list")
@csrf.exempt
def anivault_api_list():
    """Returns all anime entries as JSON for the Grid.js table."""
    user_id = request.args.get("user_id")
    
    # TODO: Task 5  - Filter by user 
    # if optional user_id parameter is empty we filter by current logged in user 

    # Current implementation (Unfiltered - returns ALL anime)
    # Sort by title (case-insensitive) then year using SQL ORDER BY
    anime_list = (
        Anime.query.filter(Anime.deleted_at.is_(None))
        .order_by(Anime.title_english.asc(), Anime.year.asc())
        .all()
    )
    return jsonify([a.to_dict() for a in anime_list])


# TASK 2: Protected Routes
@app.route("/anivault/api/jikan")
@csrf.exempt
# TODO: Task 2 - Add @login_required
def anivault_api_jikan():
    """Searches the Jikan API (MyAnimeList) and returns mapped results."""

    # Get search parameters from query string
    name = request.args.get("name", "")
    year = request.args.get("year", "")

    if not name or not year:
        return jsonify([])

    # Build the Jikan API URL
    start_date = f"{year}-01-01"
    quoted_name = quote(name)  # URL-encode the search term
    url = (
        f"https://api.jikan.moe/v4/anime?"
        f"q={quoted_name}&start_date={start_date}"
    )

    # Fetch and process API response
    try:
        with urlopen(url) as response:
            res_data = json.loads(response.read().decode())

            # Map Jikan response to our simplified format
            jikan_data = res_data.get("data", [])
            mapped_data = []
            for item in jikan_data:
                mapped_item = {
                    "mal_id": item["mal_id"],
                    "title_english": item["title_english"],
                    "image_url": item["images"]["jpg"]["image_url"],
                    "year": (
                        item.get("year")
                        or item.get("aired", {})
                        .get("prop", {})
                        .get("from", {})
                        .get("year")
                    ),
                    "episodes": item["episodes"],
                    "synopsis": item["synopsis"],
                    "score": item["score"],
                    "genres": [g["name"] for g in item["genres"]],
                }
                mapped_data.append(mapped_item)

            return jsonify(mapped_data)
    except Exception as e:
        app.logger.error(f"Jikan API Error: {e}")
        return jsonify({"error": str(e)}), 500


# TASK 6: Secure User Actions (Add)
@app.route("/anivault/api/add", methods=["POST"])
@csrf.exempt
@login_required
def anivault_api_add():
    """Adds a new anime to the collection from form data."""

    # Receive form data
    data = request.form.to_dict()
    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400

    try:
        mal_id = int(data.get("mal_id")) if data.get("mal_id") else None
    except ValueError:
        return jsonify({"success": False, "message": "Invalid mal_id"}), 400

    if not mal_id:
        return jsonify({"success": False, "message": "Missing mal_id"}), 400

    existing_anime = Anime.query.filter_by(
        mal_id=mal_id, owner_id=current_user.id
    ).first()

    if existing_anime:
        if existing_anime.deleted_at is not None:
            existing_anime.deleted_at = None
            db.session.commit()
            return jsonify(
                {"success": True, "message": "Anime restored to your vault!"}
            )
        else:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "This anime is already in your vault!",
                    }
                ),
                400,
            )

    # Create new Anime instance
    new_anime = Anime(
        mal_id=mal_id,
        title_english=data.get("title_english") or data.get("title"),
        image_url=data.get("image_url"),
        year=None,
        episodes=None,
        synopsis=data.get("synopsis"),
        score=0.0,
        my_rating=0,
        deleted_at=None,
        owner_id=current_user.id,
    )

    try:
        if data.get("year") and data.get("year") != "N/A":
            new_anime.year = int(data.get("year"))
        if data.get("episodes") and data.get("episodes") != "N/A":
            new_anime.episodes = int(data.get("episodes"))
        if data.get("score") and data.get("score") != "N/A":
            new_anime.score = float(data.get("score"))
    except ValueError:
        pass

    # --- GENRE HANDLING (Many-to-Many Relationship) ---
    # and a single Genre can be associated with many different Animes.
    # To implement this, we use an 'association table' (anime_genres)
    # that links IDs from both tables.

    genres_str = data.get("genres", "")
    if genres_str:
        # 1. Split the comma-separated string (e.g., "Action, Comedy") into a list
        genre_names = genres_str.split(",")
        for name in genre_names:
            name = name.strip()  # Remove extra whitespace
            if not name:
                continue

            # 2. Check if the Genre already exists in the database.
            # We don't want duplicate "Action" rows in the 'genres' table.
            genre = Genre.query.filter_by(name=name).first()

            # 3. If it doesn't exist, create a new Genre record.
            if not genre:
                genre = Genre(name=name)
                db.session.add(genre)  # Stage the new genre for insertion

            # SQLAlchemy handles the 'anime_genres' association table automatically
            # when we append to the 'genres' relationship list.
            new_anime.genres.append(genre)
    # --------------------------------------------------

    db.session.add(new_anime)
    db.session.commit()
    return jsonify(
        {"success": True, "message": "Successfully added to vault!"}
    )


# TASK 6: Secure User Actions (Rate)
@app.route("/anivault/api/rate", methods=["POST"])
@csrf.exempt
# TODO: Task 2 - Add @login_required
def anivault_api_rate():
    """
    Updates the user rating for an anime.
    """
    try:
        data = request.get_json()
        app.logger.info(f"Rate Data Received: {data}")
        if not data:
            return (
                jsonify(
                    {"success": False, "message": "No JSON data received"}
                ),
                400,
            )

        mal_id = data.get("mal_id")
        rating = data.get("rating")

        if mal_id is None or rating is None:
            return (
                jsonify(
                    {"success": False, "message": "Missing mal_id or rating"}
                ),
                400,
            )

        # Convert to int explicitly to be safe
        mal_id = int(mal_id)
        rating = int(rating)

        # TODO: Task 6 - Check ownership (filter by mal_id AND owner_id)
        anime = Anime.query.filter_by(mal_id=mal_id).first()

        if not anime:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Anime {mal_id} not found in vault",
                    }
                ),
                404,
            )

        anime.my_rating = rating
        db.session.commit()
        return jsonify({"success": True, "message": "Rating updated!"})
    except Exception as e:
        app.logger.error(f"Rate Error: {e}")
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# TASK 6: Secure User Actions (Delete)
@app.route("/anivault/api/delete", methods=["POST"])
@csrf.exempt
# TODO: Task 2 - Add @login_required
def anivault_api_delete():
    """
    Soft-deletes an anime from the collection.
    """
    try:
        data = request.get_json()
        app.logger.info(f"Delete Data Received: {data}")
        if not data:
            return (
                jsonify(
                    {"success": False, "message": "No JSON data received"}
                ),
                400,
            )

        mal_id = data.get("mal_id")
        if mal_id is None:
            return (
                jsonify({"success": False, "message": "Missing mal_id"}),
                400,
            )

        # Convert to int explicitly to be safe
        mal_id = int(mal_id)

        # TODO: Task 6 - Check ownership (filter by mal_id AND owner_id)
        anime = Anime.query.filter_by(mal_id=mal_id).first()

        if not anime:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": f"Anime {mal_id} not found in vault",
                    }
                ),
                404,
            )

        anime.deleted_at = datetime.utcnow()
        db.session.commit()
        return jsonify(
            {"success": True, "message": "Anime removed from collection"}
        )
    except Exception as e:
        app.logger.error(f"Delete Error: {e}")
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500