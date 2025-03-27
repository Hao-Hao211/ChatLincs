import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
from io import BytesIO
from PIL import Image
import cv2

from app.services.video.utils import (
    download_video,
    get_video_id_from_url,
    get_transcript_vtt,
    str2time,
    maintain_aspect_ratio_resize,
    encode_image,
    ollama_inference,
)

@patch("app.services.video.utils.YouTube")
@patch("app.services.video.utils.tqdm")
def test_download_video(mock_tqdm, mock_youtube):
    mock_stream = MagicMock()
    mock_stream.filesize = 100
    mock_stream.default_filename = "test_video.mp4"
    mock_youtube.return_value.streams.filter.return_value.desc.return_value.first.return_value = mock_stream

    mock_pbar = MagicMock()
    mock_tqdm.return_value = mock_pbar

    video_url = "http://youtube.com/watch?v=test"
    path = "/tmp/test"
    result = download_video(video_url, path)

    assert result == os.path.join(path, "test_video.mp4")
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
    
def test_str2time():
    time_str = "01:02:03"
    result = str2time(time_str)
    assert result == 3723000

@patch("cv2.resize")
def test_maintain_aspect_ratio_resize(mock_cv2_resize):
    image = MagicMock()
    image.shape = (100, 200, 3)
    resized_image = maintain_aspect_ratio_resize(image, width=50)
    mock_cv2_resize.assert_called_once_with(image, (50, 25), interpolation=cv2.INTER_AREA)

@patch("builtins.open", new_callable=mock_open, read_data=b"test_image_data")
def test_encode_image(mock_open_file):
    image_path = "/tmp/test_image.jpg"
    result = encode_image(image_path)
    assert result == "dGVzdF9pbWFnZV9kYXRh"

    pil_image = Image.new("RGB", (100, 100), color="white")
    result = encode_image(pil_image)
    assert isinstance(result, str)

@patch("app.services.video.utils.ollama.chat")
@patch("app.services.video.utils.encode_image")
def test_ollama_inference(mock_encode_image, mock_ollama_chat):
    mock_encode_image.return_value = "base64_image_data"
    mock_ollama_chat.return_value.message = {"content": "test_response"}

    prompt = "test_prompt"
    image = "/tmp/test_image.jpg"
    result = ollama_inference(prompt, image)

    assert result == "test_response"
    mock_encode_image.assert_called_once_with(image)
    mock_ollama_chat.assert_called_once()