
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.chat_service import file_to_base64, fileobj_to_base64, retrieve_media, generate_response_multimodal_ollama
import pytest
import base64
from unittest.mock import patch, MagicMock

def test_file_to_base64(tmp_path):
    # Create a temporary file
    file_content = b"Test content"
    temp_file = tmp_path / "test_file.txt"
    temp_file.write_bytes(file_content)

    # Convert file to base64
    result = file_to_base64(str(temp_file))

    # Check if the result is correct
    expected_result = base64.b64encode(file_content).decode('utf-8')
    assert result == expected_result

def test_file_to_base64_empty_file(tmp_path):
    # Create an empty temporary file
    temp_file = tmp_path / "empty_file.txt"
    temp_file.write_bytes(b"")

    # Convert file to base64
    result = file_to_base64(str(temp_file))

    # Check if the result is correct
    expected_result = base64.b64encode(b"").decode('utf-8')
    assert result == expected_result

def test_file_to_base64_non_existent_file():
    # Try to convert a non-existent file to base64
    with pytest.raises(FileNotFoundError):
        file_to_base64("non_existent_file.txt")


def test_fileobj_to_base64(tmp_path):
    # Create a temporary file
    file_content = b"Test content"
    temp_file = tmp_path / "test_file.txt"
    temp_file.write_bytes(file_content)

    # Open the file in read mode
    with open(temp_file, 'rb') as file_obj:
        # Convert file object to base64
        result = fileobj_to_base64(file_obj)

    # Check if the result is correct
    expected_result = base64.b64encode(file_content).decode('utf-8')
    assert result == expected_result

def test_fileobj_to_base64_empty_file(tmp_path):
    # Create an empty temporary file
    temp_file = tmp_path / "empty_file.txt"
    temp_file.write_bytes(b"")

    # Open the file in read mode
    with open(temp_file, 'rb') as file_obj:
        # Convert file object to base64
        result = fileobj_to_base64(file_obj)

    # Check if the result is correct
    expected_result = base64.b64encode(b"").decode('utf-8')
    assert result == expected_result

def test_fileobj_to_base64_non_existent_file():
    # Try to convert a non-existent file object to base64
    with pytest.raises(FileNotFoundError):
        with open("non_existent_file.txt", 'rb') as file_obj:
            fileobj_to_base64(file_obj)
            
            
def test_retrieve_media_with_text_query():
    query = "example query"
    collection_name = "example_collection"

    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_response = MagicMock()
    mock_response.objects = [MagicMock(properties={"name": "example_name", "path": "example_path"})]
    mock_collection.query.near_text.return_value = mock_response
    mock_client.collections.get.return_value = mock_collection
    mock_client.collections.list_all.return_value = [collection_name]

    with patch('weaviate.connect_to_local', return_value=mock_client):
        results = retrieve_media(query, collection_name=collection_name)

    assert len(results) == 1
    assert results[0]["name"] == "example_name"
    assert results[0]["path"] == "example_path"

def test_retrieve_media_with_uploaded_file(tmp_path):
    file_content = b"Test content"
    temp_file = tmp_path / "test_file.jpg"
    temp_file.write_bytes(file_content)

    uploaded_file = MagicMock()
    uploaded_file.filename = "test_file.jpg"
    uploaded_file.read.return_value = file_content

    query = None
    collection_name = "example_collection"

    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_response = MagicMock()
    mock_response.objects = [MagicMock(properties={"name": "example_name", "path": "example_path"})]
    mock_collection.query.near_image.return_value = mock_response
    mock_collection.query.near_media.return_value = mock_response
    mock_client.collections.get.return_value = mock_collection
    mock_client.collections.list_all.return_value = [collection_name]

    with patch('weaviate.connect_to_local', return_value=mock_client):
        results = retrieve_media(query, uploaded_file=uploaded_file, collection_name=collection_name)

    assert len(results) == 1
    assert results[0]["name"] == "example_name"
    assert results[0]["path"] == "example_path"
    
    uploaded_file.filename = "test_file.mp3"
    with patch('weaviate.connect_to_local', return_value=mock_client):
        results = retrieve_media(query, uploaded_file=uploaded_file, collection_name=collection_name)
        
    assert len(results) == 1
    assert results[0]["name"] == "example_name"
    assert results[0]["path"] == "example_path"
    
    uploaded_file.filename = "test_file.mp4"
    with patch('weaviate.connect_to_local', return_value=mock_client):
        results = retrieve_media(query, uploaded_file=uploaded_file, collection_name=collection_name)
    
    assert len(results) == 1
    assert results[0]["name"] == "example_name"
    assert results[0]["path"] == "example_path"

def test_retrieve_media_with_text_query_and_uploaded_file(tmp_path):
    file_content = b"Test content"
    temp_file = tmp_path / "test_file.jpg"
    temp_file.write_bytes(file_content)

    uploaded_file = MagicMock()
    uploaded_file.filename = "test_file.jpg"
    uploaded_file.read.return_value = file_content

    query = "example query"
    collection_name = "example_collection"

    mock_client = MagicMock()
    mock_collection = MagicMock()
    mock_response_file = MagicMock()
    mock_response_file.objects = [MagicMock(properties={"name": "example_name", "path": "example_path"})]
    mock_collection.query.near_image.return_value = mock_response_file
    mock_collection.query.near_text.return_value = mock_response_file
    mock_collection.query.near_media.return_value = mock_response_file
    mock_client.collections.get.return_value = mock_collection
    mock_client.collections.list_all.return_value = [collection_name]

    with patch('weaviate.connect_to_local', return_value=mock_client):
        results = retrieve_media(query, uploaded_file=uploaded_file, collection_name=collection_name)

    assert len(results) == 1
    assert results[0]["name"] == "example_name"
    assert results[0]["path"] == "example_path"
    
    uploaded_file.filename = "test_file.mp3"
    with patch('weaviate.connect_to_local', return_value=mock_client):
        results = retrieve_media(query, uploaded_file=uploaded_file, collection_name=collection_name)
    
    assert len(results) == 1
    assert results[0]["name"] == "example_name"
    assert results[0]["path"] == "example_path"
    
    uploaded_file.filename = "test_file.mp4"
    with patch('weaviate.connect_to_local', return_value=mock_client):
        results = retrieve_media(query, uploaded_file=uploaded_file, collection_name=collection_name)
        
    assert len(results) == 1
    assert results[0]["name"] == "example_name"
    assert results[0]["path"] == "example_path"


def test_generate_response_multimodal_ollama():
    query = "example query"
    files = [
        {"mediaType": "image", "image": "base64_image_data"},
        {"mediaType": "audio", "audio": "base64_audio_data"},
        {"mediaType": "video", "video": "base64_video_data"}
    ]
    chat_history = [{"role": "system", "content": "Welcome to the chat!"}]

    mock_response = MagicMock()
    mock_response.message = {"content": "This is a response from Ollama"}

    with patch('ollama.chat', return_value=mock_response):
        result = generate_response_multimodal_ollama(query, files, chat_history)

    assert result == "This is a response from Ollama"

def test_generate_response_multimodal_ollama_with_no_files():
    query = "example query"
    files = []
    chat_history = [{"role": "system", "content": "Welcome to the chat!"}]

    mock_response = MagicMock()
    mock_response.message = {"content": "This is a response from Ollama"}

    with patch('ollama.chat', return_value=mock_response):
        result = generate_response_multimodal_ollama(query, files, chat_history)

    assert result == "This is a response from Ollama"

def test_generate_response_multimodal_ollama_with_partial_files():
    query = "example query"
    files = [
        {"mediaType": "image", "image": "base64_image_data"},
        {"mediaType": "audio", "audio": "base64_audio_data"}
    ]
    chat_history = [{"role": "system", "content": "Welcome to the chat!"}]

    mock_response = MagicMock()
    mock_response.message = {"content": "This is a response from Ollama"}

    with patch('ollama.chat', return_value=mock_response):
        result = generate_response_multimodal_ollama(query, files, chat_history)

    assert result == "This is a response from Ollama"