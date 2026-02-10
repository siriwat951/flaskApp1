# Siriwat Tidsuksai (Armmy)
# 670510727
# sec001

import json
from urllib.request import urlopen
from urllib.parse import quote
from flask import (jsonify, render_template, request)
from app import app
import os
import datetime
from app.models.anime import Anime

DEBUG = False

@app.route('/anivault')
def anivault_mylist():
    return render_template('anivault/index.html', active_tab='search')


@app.route('/anivault/fetch')
def anivault_fetch():
    return render_template('anivault/fetch.html', active_tab='fetch')


@app.route('/anivault/api/list')
@csrf.exempt
def anivault_api_list():
    """Returns all anime entries as JSON for the Grid.js table."""
    anime_list = (
        Anime.query
        .filter(Anime.deleted_at.is_(None))
        .order_by(Anime.title_english, Anime.year)
        .all()
    )
    return jsonify([anime.to_dict() for anime in anime_list])


@app.route('/anivault/api/jikan')
def anivault_api_jikan():
    """Searches the Jikan API (MyAnimeList) and returns mapped results."""
    
    # Get search parameters from query string
    name = request.args.get('name', '')
    year = request.args.get('year', '')

    if not name or not year:
        return jsonify([])

    # Build the Jikan API URL
    start_date = f"{year}-01-01"
    quoted_name = quote(name)  # URL-encode the search term
    url = f"https://api.jikan.moe/v4/anime?q={quoted_name}&start_date={start_date}"

    # Fetch and process API response
    try:
        with urlopen(url) as response:
            res_data = json.loads(response.read().decode())

            # Map Jikan response to our simplified format
            jikan_data = res_data.get('data', [])
            mapped_data = []
            for item in jikan_data:
                mapped_item = {
                    "mal_id": item['mal_id'],
                    "title_english": item['title_english'],
                    "image_url": item['images']['jpg']['image_url'],
                    "year": item.get('year') or item.get('aired', {}).get('prop', {}).get('from', {}).get('year'),
                    "episodes": item['episodes'],
                    "synopsis": item['synopsis'],
                    "score": item['score'],
                    "genres": [g['name'] for g in item['genres']]
                }
                mapped_data.append(mapped_item)

            return jsonify(mapped_data)
    except Exception as e:
        app.logger.error(f"Jikan API Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/anivault/api/add', methods=['POST'])
@csrf.exempt
def anivault_api_add():
    """Adds a new anime to the collection from form data."""

    # Receive form data
    data = request.form.to_dict()
    if not data:
        return jsonify({'success': False, 'message': 'No data received'}), 400

    try:
        mal_id = int(data.get('mal_id')) if data.get('mal_id') else None
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid mal_id'}), 400

    if not mal_id:
        return jsonify({'success': False, 'message': 'Missing mal_id'}), 400

    existing_anime = Anime.query.filter_by(mal_id=mal_id).first()

    if existing_anime:
        if existing_anime.deleted_at is not None:
            existing_anime.deleted_at = None
            db.session.commit()
            return jsonify({'success': True, 
                            'message': 'Anime restored to your vault!'})
        else:
            return jsonify({'success': False,
                            'message': 'This anime is already in your vault!'}), 400

    # Create new Anime instance
    new_anime = Anime(
        mal_id=mal_id,
        title_english=data.get('title_english') or data.get('title'),
        image_url=data.get('image_url'),
        year=None,
        episodes=None,
        synopsis=data.get('synopsis'),
        score=0.0,
        my_rating=0,
        deleted_at=None
    )

    try:
        if data.get('year') and data.get('year') != 'N/A':
            new_anime.year = int(data.get('year'))
        if data.get('episodes') and data.get('episodes') != 'N/A':
            new_anime.episodes = int(data.get('episodes'))
        if data.get('score') and data.get('score') != 'N/A':
            new_anime.score = float(data.get('score'))
    except ValueError:
        pass

    # --- GENRE HANDLING (Many-to-Many Relationship) ---
    # and a single Genre can be associated with many different Animes.
    # To implement this, we use an 'association table' (anime_genres)
    # that links IDs from both tables.
    
    genres_str = data.get('genres', '')
    if genres_str:
        # 1. Split the comma-separated string (e.g., "Action, Comedy") into a list
        genre_names = genres_str.split(',')
        for name in genre_names:
            name = name.strip() # Remove extra whitespace
            if not name:
                continue
            
            # 2. Check if the Genre already exists in the database.
            # We don't want duplicate "Action" rows in the 'genres' table.
            genre = Genre.query.filter_by(name=name).first()
            
            # 3. If it doesn't exist, create a new Genre record.
            if not genre:
                genre = Genre(name=name)
                db.session.add(genre) # Stage the new genre for insertion
            
            # SQLAlchemy handles the 'anime_genres' association table automatically
            # when we append to the 'genres' relationship list.
            new_anime.genres.append(genre)
    # --------------------------------------------------

    db.session.add(new_anime)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Successfully added to vault!'})


@app.route('/anivault/api/rate', methods=['POST'])
# @csrf.exempt
def anivault_api_rate():
   """
   Updates the user rating for an anime.


   [STUDENT IMPLEMENTATION GUIDE]
   1. Get the JSON data from the request body.
   2. Extract 'mal_id' and 'rating'.
   3. Validate that both fields are present.
      - If missing: return jsonify({'success': False,
                                    'message': 'Missing mal_id or rating'}), 400
   4. Query the Anime model to find the entry with the matching mal_id.
      - If not found: return jsonify({'success': False,
                                      'message': 'Anime not found'}), 404
   5. If found, update the 'my_rating' field with the new value.
   6. Commit the changes to the database.
      - NOTE: For this lab, you do not need to handle complex transaction
        isolation or dirty reads.
        Assume a simple "last write wins" scenario.
   7. Return a JSON success message:
      - Success: return jsonify({'success': True,
                                 'message': 'Rating updated!'}), 200
   """

    data = request.get_json()
    if not data:
        return jsonify({'success': False,
                        'message': 'Missing mal_id or rating'}), 400

    mal_id = anime_list.query.get(mal_id)
    if not mal_id:
        return jsonify({'success': False,
                        'message': 'Anime not found'}), 404
    else:
        db.session.update('my_rating')
        db.session.commit()
        return jsonify({'success': True,
                                 'message': 'Rating updated!'}), 200



@app.route('/anivault/api/delete', methods=['POST'])
# @csrf.exempt
def anivault_api_delete():
   """
   Soft-deletes an anime from the collection.


   [STUDENT IMPLEMENTATION GUIDE]
   1. Get the JSON data from the request body.
   2. Extract 'mal_id'.
   3. Validate that 'mal_id' is present.
      - If missing: 
        return jsonify({'success': False, 'message': 'Missing mal_id'}), 400
   4. Query the Anime model to find the entry with the matching mal_id.
      - If not found: 
        return jsonify({'success': False, 'message': 'Anime not found'}), 404
   5. If found, set the 'deleted_at' field to the current timestamp
      (datetime.utcnow()).
      - DO NOT delete the row from the database!
   6. Commit the changes to the database.
   7. Return a JSON success message:
      - Success: return jsonify({'success': True,
                                 'message': 'Anime removed from collection'}), 200
   """

    result = request.get_json

    id_ = result.get('mal_id', '')

    if not id_:  # Validate ID
        app.logger.error("Error: No ID provided for removal.")
        return jsonify({'success': False, 'message': 'Missing mal_id'}), 400

    try:

        ainme = Anime.query.get(id_)
        if not anime:
            app.logger.error(f"Error: Contact with id {id_} not found.")
            return jsonify({'success': False, 'message': 'Anime not found'}), 404

        db.session.delete(anime)

        db.session.commit()  # Commit if successful
        return jsonify({'success': True,
                        'message': 'Anime removed from collection'}), 200
   pass


