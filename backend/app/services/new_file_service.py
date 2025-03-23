import weaviate
import os
import mimetypes
import base64
import sqlite3
from geopy.geocoders import Nominatim
import weaviate.classes as wvc


def initialize_database(collection_name):
    db_path = f'./databases/{collection_name}.db'
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            description TEXT,
            address TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    conn.commit()
    conn.close()

def add_media_to_database(collection_name, file_path, description, address=None, latitude=None, longitude=None):
    db_path = f'./databases/{collection_name}.db'

    if address:
        geolocator = Nominatim(user_agent="geo_app")
        location = geolocator.geocode(address)
        if location:
            latitude, longitude = location.latitude, location.longitude
        else:
            raise ValueError(f"Address not found: {address}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO media (file_path, description, address, latitude, longitude)
        VALUES (?, ?, ?, ?, ?)
    ''', (file_path, description, address, latitude, longitude))
    conn.commit()
    conn.close()

def insert_file(file, collection_name, description, address=None, latitude=None, longitude=None):
    client = weaviate.connect_to_local()

    if hasattr(file, 'read'):
        file_path = f"./uploads/{file.filename}"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(file.read())
    else:
        file_path = file

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        raise ValueError("Cannot determine MIME file type")

    if mime_type.startswith('image/'):
        file_type = "image"
        save_dir = "./uploads/image/"
    elif mime_type.startswith('audio/'):
        file_type = "audio"
        save_dir = "./uploads/audio/"
    elif mime_type.startswith('video/'):
        file_type = "video"
        save_dir = "./uploads/video/"
    else:
        raise ValueError("Not supported file type")

    os.makedirs(save_dir, exist_ok=True)
    saved_path = os.path.join(save_dir, os.path.basename(file_path))
    if not os.path.exists(saved_path):
        with open(file_path, 'rb') as src, open(saved_path, 'wb') as dest:
            dest.write(src.read())

    if not client.collections.exists(collection_name):
        client.collections.create(
            name=collection_name,
            vectorizer_config=weaviate.classes.config.Configure.Vectorizer.multi2vec_bind(
                audio_fields=["audio"],
                image_fields=["image"],
                video_fields=["video"],
            )
        )
        print(f"Collection '{collection_name}' created.")

    # Helper function to convert a file to Base64
    def to_base64(path):
        with open(path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')

    # Prepare file for insertion
    media_data = {
        "name": os.path.basename(saved_path),
        "path": saved_path,
        file_type: to_base64(saved_path),
        "mediaType": file_type,
        "collection": collection_name
    }

    # Insert the file into the collection
    print(f"Inserting {file_type} file: {media_data['name']} into collection '{collection_name}'.")
    collection = client.collections.get(collection_name)
    collection.data.insert(media_data)
    # Confirm insertion
    print(f"File '{media_data['name']}' successfully inserted into '{collection_name}'.")

    initialize_database(collection_name)
    add_media_to_database(collection_name, saved_path, description, address, latitude, longitude)
    print(f"File '{file_path}' successfully stored into '{collection_name}.db'")
    client.close()
