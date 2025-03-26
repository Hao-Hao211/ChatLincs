import base64
import io
import os
from unittest.mock import patch, MagicMock
from PIL import Image
from io import BytesIO

import pytest

from app.services.video.video_rag.embeddings.utils import (
    download_video,
    get_video_id_from_url,
    get_transcript_vtt,
    isBase64,
    encode_image,
    bt_embedding_local2
)

@patch('app.services.video.video_rag.embeddings.utils.YouTube')
@patch('app.services.video.video_rag.embeddings.utils.tqdm')
def test_download_video(mock_tqdm, mock_youtube):
    mock_stream = MagicMock()
    mock_stream.default_filename = "test_video.mp4"
    mock_stream.filesize = 1024
    mock_youtube.return_value.streams.filter.return_value.desc.return_value.first.return_value = mock_stream

    mock_pbar = MagicMock()
    mock_tqdm.return_value = mock_pbar

    video_url = "https://www.youtube.com/watch?v=test"
    path = "/tmp/test"
    result = download_video(video_url, path)

    assert result == os.path.join(path, "test_video.mp4")
    mock_youtube.assert_called_once()
    mock_stream.download.assert_called_once_with(path)
    mock_pbar.close.assert_called_once()

def test_get_video_id_from_url():
    video_url = "https://www.youtube.com/watch?v=test_id"
    result = get_video_id_from_url(video_url)
    assert result == "test_id"

    video_url = "https://youtu.be/test_id"
    result = get_video_id_from_url(video_url)
    assert result == "test_id"

    video_url = "https://www.youtube.com/embed/test_id"
    result = get_video_id_from_url(video_url)
    assert result == "test_id"

    video_url = "https://www.youtube.com/v/test_id"
    result = get_video_id_from_url(video_url)
    assert result == "test_id"
    
    video_url = "test_id"
    result = get_video_id_from_url(video_url)
    assert result == "test_id"

def test_get_transcript_vtt(tmp_path):
    video_url = "https://www.youtube.com/watch?v=test_id"
    transcript_path = tmp_path / "captions.vtt"

    with patch('app.services.video.video_rag.embeddings.utils.get_video_id_from_url', return_value="test_id"):
        with patch('app.services.video.video_rag.embeddings.utils.YouTubeTranscriptApi.get_transcript') as mock_get_transcript:
            with patch('app.services.video.video_rag.embeddings.utils.WebVTTFormatter.format_transcript') as mock_formatter:
                mock_get_transcript.return_value = [{"text": "test"}]
                mock_formatter.return_value = "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nTest"

                result = get_transcript_vtt(video_url, str(tmp_path))
                assert result == str(transcript_path)
                assert transcript_path.exists()
                
    # test when transcript file already exists
    assert get_transcript_vtt(video_url, str(tmp_path)) == str(transcript_path)

def test_isBase64_valid():
    valid_base64 = base64.b64encode(b"test string").decode('utf-8')
    assert isBase64(valid_base64) is True

def test_isBase64_invalid():
    invalid_base64 = "not_base64_string"
    assert isBase64(invalid_base64) is False
    
def test_isBase64_bytes():
    valid_base64 = base64.b64encode(b"test string")
    assert isBase64(valid_base64) is True
    
def test_isBase64_invalid_arg():
    invalid_base64 = 14234256
    assert isBase64(invalid_base64) is False

@patch('app.services.video.video_rag.embeddings.utils.BridgeTowerProcessor.from_pretrained')
@patch('app.services.video.video_rag.embeddings.utils.BridgeTowerForContrastiveLearning.from_pretrained')
def test_bt_embedding_local2_with_valid_base64_image(mock_model, mock_processor):
    # Mock processor and model
    mock_processor_instance = MagicMock()
    mock_processor.return_value = mock_processor_instance
    mock_model_instance = MagicMock()
    mock_model.return_value = mock_model_instance

    # Mock outputs
    mock_model_instance.return_value = MagicMock()
    mock_model_instance.return_value.text_embeds = MagicMock()
    mock_model_instance.return_value.text_embeds[0].detach.return_value.cpu.return_value.numpy.return_value.tolist.return_value = [0.1, 0.2, 0.3]

    # Create a valid base64 image
    img = Image.new("RGB", (100, 100), color="red")
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # Call the function
    prompt = "Test prompt"
    result = bt_embedding_local2(prompt, base64_image)

    # Assertions
    assert result == [0.1, 0.2, 0.3]
    mock_processor.assert_called_once_with("BridgeTower/bridgetower-large-itm-mlm-itc")
    mock_model.assert_called_once_with("BridgeTower/bridgetower-large-itm-mlm-itc")
    mock_processor_instance.tokenizer.assert_called_once_with(prompt, return_tensors="pt", truncation=True, max_length=400)

@patch('app.services.video.video_rag.embeddings.utils.BridgeTowerProcessor.from_pretrained')
@patch('app.services.video.video_rag.embeddings.utils.BridgeTowerForContrastiveLearning.from_pretrained')
def test_bt_embedding_local2_with_invalid_base64_image(mock_model, mock_processor):
    # Mock processor and model
    mock_processor_instance = MagicMock()
    mock_processor.return_value = mock_processor_instance
    mock_model_instance = MagicMock()
    mock_model.return_value = mock_model_instance

    # Invalid base64 image
    invalid_base64_image = "invalid_base64_string"

    # Call the function and expect a TypeError
    prompt = "Test prompt"
    with pytest.raises(TypeError, match="image input must be in base64 encoding!"):
        bt_embedding_local2(prompt, invalid_base64_image)

    # Assertions
    mock_processor.assert_called_once_with("BridgeTower/bridgetower-large-itm-mlm-itc")
    mock_model.assert_called_once_with("BridgeTower/bridgetower-large-itm-mlm-itc")

@patch('app.services.video.video_rag.embeddings.utils.BridgeTowerProcessor.from_pretrained')
@patch('app.services.video.video_rag.embeddings.utils.BridgeTowerForContrastiveLearning.from_pretrained')
def test_bt_embedding_local2_without_image(mock_model, mock_processor):
    # Mock processor and model
    mock_processor_instance = MagicMock()
    mock_processor.return_value = mock_processor_instance
    mock_model_instance = MagicMock()
    mock_model.return_value = mock_model_instance

    # Mock outputs
    mock_model_instance.return_value = MagicMock()
    mock_model_instance.return_value.text_embeds = MagicMock()
    mock_model_instance.return_value.text_embeds[0].detach.return_value.cpu.return_value.numpy.return_value.tolist.return_value = [0.4, 0.5, 0.6]

    # Call the function without an image
    prompt = "Test prompt"
    result = bt_embedding_local2(prompt, None)

    # Assertions
    assert result == [0.4, 0.5, 0.6]
    mock_processor.assert_called_once_with("BridgeTower/bridgetower-large-itm-mlm-itc")
    mock_model.assert_called_once_with("BridgeTower/bridgetower-large-itm-mlm-itc")
    mock_processor_instance.tokenizer.assert_called_once_with(prompt, return_tensors="pt", truncation=True, max_length=400)
    
@patch('builtins.open', new_callable=MagicMock)
def test_encode_image_from_path(mock_open):
    mock_open.return_value.__enter__.return_value.read.return_value = b"image content"
    result = encode_image("path/to/image.jpg")
    assert isinstance(result, str)
    assert base64.b64decode(result) == b"image content"

def test_encode_image_from_pil():
    img = Image.new("RGB", (100, 100), color="red")
    result = encode_image(img)
    assert isinstance(result, str)
    decoded_image = Image.open(BytesIO(base64.b64decode(result)))
    assert decoded_image.size == (100, 100)
    assert decoded_image.mode == "RGB"