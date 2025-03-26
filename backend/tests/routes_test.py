from io import BytesIO
import os
import base64
import tempfile
import warnings
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.routes import app, api_bp, transcribe_audio

'''
# upload() : POST /upload

@patch('app.routes.insert_file_into_collection')
def test_upload_success(mock_insert_file, client):
    data = {
        'file': (MagicMock(filename='test.txt'), 'test.txt'),
        'collection_name': 'test_collection'
    }
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"success" in response.data

@patch('app.routes.insert_file_into_collection')
def test_upload_no_file(mock_insert_file, client):
    data = {'collection_name': 'test_collection'}
    response = client.post('/upload', data=data)
    assert response.status_code == 400
    assert b"No file part in the request" in response.data

@patch('app.routes.insert_file_into_collection')
def test_upload_no_collection_name(mock_insert_file, client):
    data = {'file': (MagicMock(filename='test.txt'), 'test.txt')}
    response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"No collection name provided" in response.data


# chat() : POST /chat

@patch('app.routes.retrieve_media')
@patch('app.routes.generate_response_multimodal_ollama')
def test_chat_success(mock_generate_response, mock_retrieve_media, client):
    mock_generate_response.return_value = "Test response"
    mock_retrieve_media.return_value = []

    data = {
        'query': 'test query',
        'collection_name': 'test_collection',
        'retrieve': 'false',
        'session_id': 'default'
    }
    response = client.post('/chat', data=data)
    assert response.status_code == 200
    assert b"Test response" in response.data

@patch('app.routes.retrieve_media')
@patch('app.routes.generate_response_multimodal_ollama')
def test_chat_no_query(mock_generate_response, mock_retrieve_media, client):
    data = {
        'collection_name': 'test_collection',
        'retrieve': 'false',
        'session_id': 'default'
    }
    response = client.post('/chat', data=data)
    assert response.status_code == 400
    assert b"Please provide a query." in response.data


# geo_search() : GET /geo_search


@patch('app.routes.search_nearby')
@patch('app.routes.create_map')
@patch('app.routes.save_map')
def test_geo_search_success(mock_save_map, mock_create_map, mock_search_nearby, client):
    mock_search_nearby.return_value = []
    mock_create_map.return_value = MagicMock()

    response = client.get('/geo_search?address=test_address&radius=2')
    assert response.status_code == 200

@patch('app.routes.search_nearby')
def test_geo_search_no_address(mock_search_nearby, client):
    response = client.get('/geo_search?radius=2')
    assert response.status_code == 400
    assert b"Please provide an address." in response.data

'''
# get_collections() : GET /collections


@patch('app.routes.weaviate.connect_to_local')
def test_get_collections_success(mock_connect_to_local, client):
    mock_client = MagicMock()
    mock_client.collections.list_all.return_value = {'collection1': {}, 'collection2': {}}
    mock_connect_to_local.return_value = mock_client

    response = client.get('/collections')
    assert response.status_code == 200
    assert b"collection1" in response.data
    assert b"collection2" in response.data


# new_upload() : POST /new_upload


@patch('app.routes.insert_file')
def test_new_upload_success(mock_insert_file, client):
    data = {
        'file': (MagicMock(filename='test.txt'), 'test.txt'),
        'collection_name': 'test_collection',
        'description': 'test description'
    }
    response = client.post('/new_upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"success" in response.data

@patch('app.routes.insert_file')
def test_new_upload_no_file(mock_insert_file, client):
    data = {'collection_name': 'test_collection'}
    response = client.post('/new_upload', data=data)
    assert response.status_code == 400
    assert b"No file part in the request" in response.data

@patch('app.routes.insert_file')
def test_new_upload_manual_latitude_longitude(mock_insert_file, client):
    test_latitude = 51.5285582
    test_longitude = -0.2416815
    data = {
        'file': (MagicMock(filename='test.txt'), 'test.txt'),
        'collection_name': 'test_collection',
        'description': 'test description',
        'latitude': test_latitude,
        'longitude': test_longitude
    }
    response = client.post('/new_upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"success" in response.data

'''
# new_geo_search() : GET /new_geo_search


@patch('app.routes.new_search_nearby')
def test_new_geo_search_success(mock_new_search_nearby, client):
    mock_new_search_nearby.return_value = {"results": []}

    response = client.get('/new_geo_search?collection_name=test_collection&radius=2')
    assert response.status_code == 200

@patch('app.routes.new_search_nearby')
def test_new_geo_search_no_collection_name(mock_new_search_nearby, client):
    response = client.get('/new_geo_search?radius=2')
    assert response.status_code == 400
    assert b"Please provide a collection name." in response.data
    
@patch('app.routes.new_search_nearby')
def test_new_geo_search_manual_latitude_longitude(mock_new_search_nearby, client):
    test_latitude = 51.5285582
    test_longitude = -0.2416815
    response = client.get(f'/new_geo_search?collection_name=test_collection&latitude={test_latitude}&longitude={test_longitude}&radius=2')
    assert response.status_code == 200

'''
    
# geo_map() : GET /geo_map


@patch('app.routes.new_search_nearby')
@patch('app.routes.create_geo_map')
@patch('app.routes.save_geo_map')
def test_geo_map_success(mock_save_geo_map, mock_create_geo_map, mock_new_search_nearby, client):
    mock_new_search_nearby.return_value = {"results": [{"name": "Test Place"}]}
    mock_create_geo_map.return_value = MagicMock()

    response = client.get('/geo_map?collection_name=test_collection&radius=2')
    assert response.status_code == 200

@patch('app.routes.new_search_nearby')
def test_geo_map_no_collection_name(mock_new_search_nearby, client):
    response = client.get('/geo_map?radius=2')
    assert response.status_code == 400
    assert b"Please provide a collection name." in response.data

@patch('app.routes.new_search_nearby')
@patch('app.routes.create_empty_map')
@patch('app.routes.save_geo_map')
def test_geo_map_no_results(mock_save_geo_map, mock_create_empty_map, mock_new_search_nearby, client):
    mock_new_search_nearby.return_value = {"results": []}
    mock_create_empty_map.return_value = MagicMock()

    response = client.get('/geo_map?collection_name=test_collection&radius=2')
    assert response.status_code == 200
    
@patch('app.routes.new_search_nearby')
def test_geo_map_manual_latitude_longitude(mock_new_search_nearby, client):
    test_latitude = 51.5285582
    test_longitude = -0.2416815
    response = client.get(f'/geo_map?collection_name=test_collection&latitude={test_latitude}&longitude={test_longitude}&radius=2')
    assert response.status_code == 200
    
    
# uploaded_file() : GET /uploads/<path:filename>


def test_uploaded_file_success(client):
    # Create a temporary file in the uploads directory
    upload_folder = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    temp_file_path = os.path.join(upload_folder, 'test_file.txt')
    with open(temp_file_path, 'w') as temp_file:
        temp_file.write('This is a test file.')

    response = client.get('/uploads/test_file.txt')
    assert response.status_code == 200
    assert b'This is a test file.' in response.data

    # Clean up the temporary file
    try:
        os.remove(temp_file_path)
    except:
        warnings.warn(UserWarning("Failed to clean up temporary file at " + temp_file_path + "\nNote: this has no impact on the test results."))
    
def test_uploaded_file_not_found(client):
    response = client.get('/uploads/non_existent_file.txt')
    assert response.status_code == 404


# chat() : POST /chat


@patch('app.routes.retrieve_media')
@patch('app.routes.generate_response_multimodal_ollama')
def test_chat_success(mock_generate_response, mock_retrieve_media, client):
    mock_generate_response.return_value = "Test response"
    mock_retrieve_media.return_value = []

    data = {
        'query': 'test query',
        'collection_name': 'test_collection',
        'retrieve': 'false',
        'session_id': 'default'
    }
    response = client.post('/chat', data=data)
    assert response.status_code == 200
    assert b"Test response" in response.data

@patch('app.routes.retrieve_media')
@patch('app.routes.generate_response_multimodal_ollama')
def test_chat_no_query(mock_generate_response, mock_retrieve_media, client):
    data = {
        'collection_name': 'test_collection',
        'retrieve': 'false',
        'session_id': 'default'
    }
    response = client.post('/chat', data=data)
    assert response.status_code == 400
    assert b"Please provide a query." in response.data

@patch('app.routes.retrieve_media')
@patch('app.routes.generate_response_multimodal_ollama')
def test_chat_with_uploaded_file(mock_generate_response, mock_retrieve_media, client):
    mock_generate_response.return_value = "Test response"
    mock_retrieve_media.return_value = []

    data = {
        'query': 'test query',
        'collection_name': 'test_collection',
        'retrieve': 'true',
        'session_id': 'default',
        'uploaded_file': (BytesIO(b"test file content"), 'test_file.txt')
    }
    response = client.post('/chat', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert b"Test response" in response.data

@patch('app.routes.retrieve_media')
@patch('app.routes.transcribe_audio')
@patch('app.routes.generate_response_multimodal_ollama')
def test_chat_with_audio_transcription(mock_generate_response, mock_transcribe_audio, mock_retrieve_media, client):
    mock_generate_response.return_value = "Test response"
    mock_transcribe_audio.return_value = "test audio transcription"
    mock_retrieve_media.return_value = [{
        "mediaType": "audio",
        "audio": base64.b64encode(b"test audio content").decode('utf-8')
    }]

    data = {
        'query': 'test query',
        'collection_name': 'test_collection',
        'retrieve': 'true',
        'session_id': 'default'
    }
    response = client.post('/chat', data=data)
    assert response.status_code == 200
    assert b"Test response" in response.data
    

# transcribe_audio() : auxiliary function


@patch('app.routes.whisper.load_model')
def test_transcribe_audio_success(mock_load_model):
    mock_model = MagicMock()
    mock_load_model.return_value = mock_model
    mock_model.transcribe.return_value = {"text": "test transcription"}

    base64_audio = base64.b64encode(b"test audio content").decode('utf-8')
    transcript = transcribe_audio(base64_audio)

    assert transcript == "test transcription"
    mock_load_model.assert_called_once()
    mock_model.transcribe.assert_called_once()

@patch('app.routes.whisper.load_model')
def test_transcribe_audio_no_text(mock_load_model):
    mock_model = MagicMock()
    mock_load_model.return_value = mock_model
    mock_model.transcribe.return_value = {}

    base64_audio = base64.b64encode(b"test audio content").decode('utf-8')
    transcript = transcribe_audio(base64_audio)

    assert transcript == ""
    mock_load_model.assert_called_once_with("small")
    mock_model.transcribe.assert_called_once()

@patch('app.routes.whisper.load_model')
def test_transcribe_audio_exception(mock_load_model):
    mock_model = MagicMock()
    mock_load_model.return_value = mock_model
    mock_model.transcribe.side_effect = Exception("Transcription error")

    base64_audio = base64.b64encode(b"test audio content").decode('utf-8')

    with pytest.raises(Exception) as excinfo:
        transcribe_audio(base64_audio)

    assert "Transcription error" in str(excinfo.value)
    mock_load_model.assert_called_once_with("small")
    mock_model.transcribe.assert_called_once()

'''
# upload_video() : POST /upload_video


@patch('app.routes.video_service.download_video')
@patch('app.routes.video_service.get_transcript_vtt')
@patch('app.routes.extract_and_save_frames_and_metadata_with_fps')
def test_upload_video_without_language_sound(mock_extract_frames, mock_get_transcript, mock_download_video, client):
    mock_download_video.return_value = './shared_data/videos/test_video.mp4'
    mock_get_transcript.return_value = None
    mock_extract_frames.return_value = []

    data = {
        'video_url': 'https://example.com/test_video',
        'video_without_language_sound': 'true'
    }
    response = client.post('/upload_video', data=data)

    assert response.status_code == 200
    assert b"success" in response.data
    mock_download_video.assert_called_once_with('https://example.com/test_video', './shared_data/videos/test_video')
    mock_extract_frames.assert_called_once()

@patch('app.routes.video_service.download_video')
@patch('app.routes.video_service.get_transcript_vtt')
@patch('app.routes.extract_and_save_frames_and_metadata')
def test_upload_video_with_transcript(mock_extract_frames, mock_get_transcript, mock_download_video, client):
    mock_download_video.return_value = './shared_data/videos/test_video.mp4'
    mock_get_transcript.return_value = './shared_data/videos/test_video_transcript.vtt'
    mock_extract_frames.return_value = []

    data = {
        'video_url': 'https://example.com/test_video',
        'video_without_language_sound': 'false'
    }
    response = client.post('/upload_video', data=data)

    assert response.status_code == 200
    assert b"success" in response.data
    mock_download_video.assert_called_once_with('https://example.com/test_video', './shared_data/videos/test_video')
    mock_get_transcript.assert_called_once_with('https://example.com/test_video', './shared_data/videos/test_video')
    mock_extract_frames.assert_called_once()

@patch('app.routes.video_service.download_video')
@patch('app.routes.video_service.get_transcript_vtt')
@patch('app.routes.whisper.load_model')
@patch('app.routes.extract_and_save_frames_and_metadata')
def test_upload_video_generate_transcript(mock_extract_frames, mock_load_model, mock_get_transcript, mock_download_video, client):
    mock_download_video.return_value = './shared_data/videos/test_video.mp4'
    mock_get_transcript.return_value = None
    mock_model = MagicMock()
    mock_load_model.return_value = mock_model
    mock_model.transcribe.return_value = {"segments": [{"text": "test transcript"}]}
    mock_extract_frames.return_value = []

    data = {
        'video_url': 'https://example.com/test_video',
        'video_without_language_sound': 'false'
    }
    response = client.post('/upload_video', data=data)

    assert response.status_code == 200
    assert b"success" in response.data
    mock_download_video.assert_called_once_with('https://example.com/test_video', './shared_data/videos/test_video')
    mock_get_transcript.assert_called_once_with('https://example.com/test_video', './shared_data/videos/test_video')
    mock_load_model.assert_called_once_with("small")
    mock_model.transcribe.assert_called_once()
    mock_extract_frames.assert_called_once()

@patch('app.routes.video_service.download_video')
def test_upload_video_missing_url(mock_download_video, client):
    data = {
        'video_without_language_sound': 'false'
    }
    response = client.post('/upload_video', data=data)

    assert response.status_code == 400
    assert b"video_url" in response.data
    mock_download_video.assert_not_called()
'''