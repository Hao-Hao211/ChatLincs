import base64
import pytest
from unittest.mock import patch, MagicMock
from app.services.video.video_rag.MLM.utils import isBase64, encode_image_from_path_or_url, ollama_inference_without64

# Test for isBase64 function
def test_isBase64_valid_base64_string():
    valid_base64 = base64.b64encode(b"test string").decode('utf-8')
    assert isBase64(valid_base64) is True

def test_isBase64_invalid_base64_string():
    invalid_base64 = "not_base64_string"
    assert isBase64(invalid_base64) is False

def test_isBase64_bytes_input():
    valid_base64_bytes = base64.b64encode(b"test string")
    assert isBase64(valid_base64_bytes) is True

def test_isBase64_invalid_input_type():
    assert isBase64(12345) is False  # Invalid input type

# Test for encode_image_from_path_or_url function
@patch('app.services.video.video_rag.MLM.utils.urlopen')
@patch('app.services.video.video_rag.MLM.utils.requests.get')
def test_encode_image_from_url(mock_requests_get, mock_urlopen):
    mock_requests_get.return_value.content = b"image content"
    mock_urlopen.return_value = MagicMock()
    result = encode_image_from_path_or_url("http://example.com/image.jpg")
    assert isinstance(result, str)
    assert base64.b64decode(result) == b"image content"

@patch('builtins.open', new_callable=MagicMock)
def test_encode_image_from_path(mock_open):
    mock_open.return_value.__enter__.return_value.read.return_value = b"image content"
    result = encode_image_from_path_or_url("path/to/image.jpg")
    assert isinstance(result, str)
    assert base64.b64decode(result) == b"image content"

@patch('app.services.video.video_rag.MLM.utils.urlopen')
def test_encode_image_from_invalid_url(mock_urlopen):
    mock_urlopen.side_effect = Exception("Invalid URL")
    with pytest.raises(Exception):
        encode_image_from_path_or_url("http://invalid-url.com/image.jpg")

# Test for ollama_inference_without64 function
@patch('app.services.video.video_rag.MLM.utils.ollama.chat')
def test_ollama_inference_without64(mock_ollama_chat):
    mock_ollama_chat.return_value.message = {'content': 'Test response'}
    result = ollama_inference_without64("Test prompt", "base64_image_string")
    assert result == "Test response"
    mock_ollama_chat.assert_called_once_with(
        model='llava:7b',
        messages=[{
            'role': 'user',
            'content': "Test prompt",
            'images': ["base64_image_string"]
        }]
    )