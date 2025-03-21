import os
import pytest
import mimetypes
from unittest.mock import patch, MagicMock, mock_open
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.file_service import insert_file_into_collection

@patch('app.services.file_service.weaviate.connect_to_local')
@patch('builtins.open', new_callable=mock_open, read_data=b'test data')
@patch('os.makedirs')
@patch('os.path.exists', return_value=False)
@patch('mimetypes.guess_type', return_value=('image/jpeg', None))
def test_insert_file_into_collection_success(mock_guess_type, mock_exists, mock_makedirs, mock_open, mock_connect):
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_client.collections.exists.return_value = False
    mock_collection = MagicMock()
    mock_client.collections.get.return_value = mock_collection

    file = MagicMock()
    file.filename = 'test.jpg'
    collection_name = 'test_collection'

    insert_file_into_collection(file, collection_name)

    mock_client.collections.create.assert_called()
    mock_collection.data.insert.assert_called()

@patch('app.services.file_service.weaviate.connect_to_local')
@patch('builtins.open', new_callable=mock_open, read_data=b'test data')
@patch('os.makedirs')
@patch('os.path.exists', return_value=False)
@patch('mimetypes.guess_type', return_value=(None, None))
def test_insert_file_into_collection_no_mime_type(mock_guess_type, mock_exists, mock_makedirs, mock_open, mock_connect):
    mock_client = MagicMock()
    mock_connect.return_value = mock_client

    file = MagicMock()
    file.filename = 'test.unknown'
    collection_name = 'test_collection'

    with pytest.raises(ValueError, match="Unable to determine the MIME type of the file"):
        insert_file_into_collection(file, collection_name)

    mock_client.collections.create.assert_not_called()
    mock_client.collections.get.assert_not_called()

@patch('app.services.file_service.weaviate.connect_to_local')
@patch('builtins.open', new_callable=mock_open, read_data=b'test data')
@patch('os.makedirs')
@patch('os.path.exists', return_value=False)
@patch('mimetypes.guess_type', return_value=('application/pdf', None))
def test_insert_file_into_collection_unsupported_mime_type(mock_guess_type, mock_exists, mock_makedirs, mock_open, mock_connect):
    mock_client = MagicMock()
    mock_connect.return_value = mock_client

    file = MagicMock()
    file.filename = 'test.pdf'
    collection_name = 'test_collection'

    with pytest.raises(ValueError, match="Unsupported file type for MIME type"):
        insert_file_into_collection(file, collection_name)

    mock_client.collections.create.assert_not_called()
    mock_client.collections.get.assert_not_called()

@patch('app.services.file_service.weaviate.connect_to_local')
@patch('builtins.open', new_callable=mock_open, read_data=b'test data')
@patch('os.makedirs')
@patch('os.path.exists', return_value=False)
@patch('mimetypes.guess_type', return_value=('image/jpeg', None))
def test_insert_file_into_collection_collection_exists(mock_guess_type, mock_exists, mock_makedirs, mock_open, mock_connect):
    mock_client = MagicMock()
    mock_connect.return_value = mock_client
    mock_client.collections.exists.return_value = True
    mock_collection = MagicMock()
    mock_client.collections.get.return_value = mock_collection

    file = MagicMock()
    file.filename = 'test.jpg'
    collection_name = 'test_collection'

    insert_file_into_collection(file, collection_name)

    mock_client.collections.create.assert_not_called()
    mock_collection.data.insert.assert_called()