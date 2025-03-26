import os
import sqlite3
import pytest
from unittest.mock import patch, MagicMock
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.new_geo import new_initialize_database, new_search_nearby

@pytest.fixture
def mock_db_path():
    return './databases/test_collection.db'

@pytest.fixture
def setup_database(mock_db_path):
    os.makedirs(os.path.dirname(mock_db_path), exist_ok=True)
    conn = sqlite3.connect(mock_db_path)
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
    yield
    os.remove(mock_db_path)



def test_new_initialize_database(mock_db_path):
    new_initialize_database('test_collection')
    assert os.path.exists(mock_db_path)



@patch('app.services.new_geo.Nominatim')
@patch('app.services.new_geo.sqlite3.connect')
def test_new_search_nearby_success(mock_connect, mock_nominatim, setup_database):
    mock_geolocator = MagicMock()
    mock_nominatim.return_value = mock_geolocator
    mock_geolocator.geocode.return_value = MagicMock(latitude=51.5285582, longitude=-0.2416815)

    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (1, 'path/to/file', 'description', 'address', 51.5285582, -0.2416815)
    ]

    result = new_search_nearby('test_collection', address="The Regent's Park", radius_km=2)
    assert 'results' in result
    assert len(result['results']) == 1

@patch('app.services.new_geo.Nominatim')
def test_new_search_nearby_invalid_address(mock_nominatim, setup_database):
    mock_geolocator = MagicMock()
    mock_nominatim.return_value = mock_geolocator
    mock_geolocator.geocode.return_value = None

    result = new_search_nearby('test_collection', address="Invalid Address", radius_km=2)
    assert 'error' in result
    assert result['error'] == "Address not found: Invalid Address"

@patch('app.services.new_geo.Nominatim')
@patch('app.services.new_geo.sqlite3.connect')
def test_new_search_nearby_no_results(mock_connect, mock_nominatim, setup_database):
    mock_geolocator = MagicMock()
    mock_nominatim.return_value = mock_geolocator
    mock_geolocator.geocode.return_value = MagicMock(latitude=51.5285582, longitude=-0.2416815)

    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []

    result = new_search_nearby('test_collection', address="The Regent's Park", radius_km=2)
    assert 'results' in result
    assert len(result['results']) == 0

def test_new_search_nearby_non_existent_collection():
    result = new_search_nearby('non_existent_collection', address="The Regent's Park", radius_km=2)
    assert 'error' in result
    assert result['error'] == "Collection 'non_existent_collection' does not exist."