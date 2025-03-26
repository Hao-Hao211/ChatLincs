import pytest
import warnings
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.new_file_service import initialize_database, add_media_to_database, insert_file


def test_initialize_database():
    collection_name = 'test_collection'

    initialize_database(collection_name)

    assert os.path.exists(f'./databases/{collection_name}.db')
    
    try:
        os.rmdir(f'./databases')
    except:
        warnings.warn(UserWarning(f'Failed to remove directory "./databases". Note: this does not affect the test result.'))
        pass
    

@patch('app.services.new_file_service.sqlite3.connect')
@patch('app.services.new_file_service.Nominatim.geocode')
def test_add_media_to_database_with_address(mock_geocode, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_geocode.return_value = MagicMock(latitude=51.5285582, longitude=-0.2416815)

    collection_name = 'test_collection'
    file_path = 'test_path'
    description = 'test_description'
    address = 'The Regent\'s Park, London'

    add_media_to_database(collection_name, file_path, description, address=address)

    mock_connect.assert_called_with(f'./databases/{collection_name}.db')
    mock_cursor.execute.assert_called_with(
        '''
        INSERT INTO media (file_path, description, address, latitude, longitude)
        VALUES (?, ?, ?, ?, ?)
    ''', (file_path, description, address, 51.5285582, -0.2416815)
    )
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called()

@patch('app.services.new_file_service.sqlite3.connect')
def test_add_media_to_database_without_address(mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    collection_name = 'test_collection'
    file_path = 'test_path'
    description = 'test_description'

    add_media_to_database(collection_name, file_path, description)

    mock_connect.assert_called_with(f'./databases/{collection_name}.db')
    mock_cursor.execute.assert_called_with(
        '''
        INSERT INTO media (file_path, description, address, latitude, longitude)
        VALUES (?, ?, ?, ?, ?)
    ''', (file_path, description, None, None, None)
    )
    mock_conn.commit.assert_called()
    mock_conn.close.assert_called()

@patch('app.services.new_file_service.sqlite3.connect')
@patch('app.services.new_file_service.Nominatim.geocode')
def test_add_media_to_database_invalid_address(mock_geocode, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_geocode.return_value = None

    collection_name = 'test_collection'
    file_path = 'test_path'
    description = 'test_description'
    address = 'Invalid Address'

    with pytest.raises(ValueError, match="Address not found: Invalid Address"):
        add_media_to_database(collection_name, file_path, description, address=address)

    mock_connect.assert_not_called()
    mock_cursor.execute.assert_not_called()
    mock_conn.commit.assert_not_called()
    mock_conn.close.assert_not_called()
    

# insert_file() tests


@patch('app.services.new_file_service.weaviate.connect_to_local')
@patch('builtins.open', new_callable=mock_open, read_data=b'test data')
@patch('os.makedirs')
@patch('os.path.exists', return_value=False)
@patch('app.services.new_file_service.add_media_to_database')
@patch('app.services.new_file_service.initialize_database')
def test_insert_file_success(mock_initialize_database, mock_add_media_to_database, mock_exists, mock_makedirs, mock_open, mock_connect):
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_client.collections.exists.return_value = False
    mock_collection = MagicMock()
    mock_client.collections.get.return_value = mock_collection

    file = MagicMock()
    file.filename = 'test.jpg'
    collection_name = 'test_collection' 
    description = 'test_description'
    address = 'The Regent\'s Park, London'

    insert_file(file, collection_name, description, address=address)

    mock_client.collections.create.assert_called()
    mock_collection.data.insert.assert_called()
    mock_initialize_database.assert_called_with(collection_name)
    mock_add_media_to_database.assert_called()
    
    file.filename = 'test.mp3'
    insert_file(file, collection_name, description, address=address)
    mock_client.collections.create.assert_called()
    mock_collection.data.insert.assert_called()
    mock_initialize_database.assert_called_with(collection_name)
    mock_add_media_to_database.assert_called()
    
    file.filename = 'test.mp4'
    insert_file(file, collection_name, description, address=address)
    mock_client.collections.create.assert_called()
    mock_collection.data.insert.assert_called()
    mock_initialize_database.assert_called_with(collection_name)
    mock_add_media_to_database.assert_called()

@patch('app.services.new_file_service.weaviate.connect_to_local')
@patch('builtins.open', new_callable=mock_open, read_data=b'test data')
@patch('os.makedirs')
@patch('os.path.exists', return_value=False)
@patch('mimetypes.guess_type', return_value=(None, None))
def test_insert_file_no_mime_type(mock_guess_type, mock_exists, mock_makedirs, mock_open, mock_connect):
    mock_client = MagicMock()
    mock_connect.return_value = mock_client

    file = MagicMock()
    file.filename = 'test.unknown'
    collection_name = 'test_collection'
    description = 'test_description'

    with pytest.raises(ValueError, match="Cannot determine MIME type of file"):
        insert_file(file, collection_name, description)

    mock_client.collections.create.assert_not_called()

@patch('app.services.new_file_service.weaviate.connect_to_local')
@patch('builtins.open', new_callable=mock_open, read_data=b'test data')
@patch('os.makedirs')
@patch('os.path.exists', return_value=False)
@patch('mimetypes.guess_type', return_value=('application/pdf', None))
def test_insert_file_unsupported_mime_type(mock_guess_type, mock_exists, mock_makedirs, mock_open, mock_connect):
    mock_client = MagicMock()
    mock_connect.return_value = mock_client

    file = MagicMock()
    file.filename = 'test.pdf'
    collection_name = 'test_collection'
    description = 'test_description'

    with pytest.raises(ValueError, match="Not supported file type"):
        insert_file(file, collection_name, description)

    mock_client.collections.create.assert_not_called()

@patch('app.services.new_file_service.weaviate.connect_to_local')
@patch('builtins.open', new_callable=mock_open, read_data=b'test data')
@patch('os.makedirs')
@patch('os.path.exists', return_value=False)
@patch('mimetypes.guess_type', return_value=('image/jpeg', None))
@patch('app.services.new_file_service.add_media_to_database')
@patch('app.services.new_file_service.initialize_database')
def test_insert_file_collection_exists(mock_initialize_database, mock_add_media_to_database, mock_guess_type, mock_exists, mock_makedirs, mock_open, mock_connect):
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_client.collections.exists.return_value = True
    mock_collection = MagicMock()
    mock_client.collections.get.return_value = mock_collection

    file = MagicMock()
    file.filename = 'test.jpg'
    collection_name = 'test_collection'
    description = 'test_description'
    address = 'The Regent\'s Park, London'

    insert_file(file, collection_name, description, address=address)

    mock_client.collections.create.assert_not_called()
    mock_collection.data.insert.assert_called()
    mock_initialize_database.assert_called_with(collection_name)
    mock_add_media_to_database.assert_called()

