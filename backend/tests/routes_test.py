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

'''
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

'''
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
