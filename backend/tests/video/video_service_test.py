import pytest
import json
import os
from youtube_transcript_api import VideoUnavailable, NoTranscriptFound
from unittest.mock import patch, MagicMock, mock_open, ANY
from app.services.video.video_service import (
    load_json_file,
    get_video_id_from_url,
    download_video,
    get_transcript_vtt,
    format_timestamp,
    _processText,
    write_vtt,
    getSubs,
    write_srt,
    extract_and_save_frames_and_metadata,
    extract_and_save_frames_and_metadata_with_fps,
    clean_table_name,
    get_youtube_title,
    prompt_processing,
    encode_image_to_base64,
)

# Test load_json_file
def test_load_json_file():
    mock_data = {"key": "value"}
    with patch("builtins.open", mock_open(read_data='{"key": "value"}')) as mock_file:
        result = load_json_file("test.json")
        assert result == mock_data
        mock_file.assert_called_once_with("test.json", "r")

# Test get_video_id_from_url
@pytest.mark.parametrize(
    "video_url, expected_id",
    [
        ("https://youtu.be/abc123", "abc123"),
        ("https://www.youtube.com/watch?v=abc123", "abc123"),
        ("https://www.youtube.com/embed/abc123", "abc123"),
        ("https://www.youtube.com/v/abc123", "abc123"),
    ],
)
def test_get_video_id_from_url(video_url, expected_id):
    result = get_video_id_from_url(video_url)
    assert result == expected_id
    
'''
# Test download_video_with_filecheck
@patch("app.services.video.video_service.YouTube")
@patch("app.services.video.video_service.glob.glob")
@patch("os.path.exists")
@patch("os.makedirs")
def test_download_video_with_filecheck(mock_makedirs, mock_exists, mock_glob, mock_youtube):
    mock_glob.return_value = []
    mock_exists.return_value = False
    mock_stream = MagicMock()
    mock_stream.default_filename = "test.mp4"
    mock_stream.filesize = 1024
    mock_youtube.return_value.streams.filter.return_value.desc.return_value.first.return_value = mock_stream

    with patch("builtins.open", mock_open()) as mock_file, patch("tqdm.tqdm") as mock_tqdm:
        mock_tqdm.return_value = MagicMock()
        result = download_video_with_filecheck("https://youtu.be/abc123", "/tmp/")
        assert result == "/tmp/test.mp4"
        mock_makedirs.assert_called_once_with("/tmp/")
'''

# Test download_video

@patch("app.services.video.video_service.YouTube")
@patch("app.services.video.video_service.glob.glob")
@patch("os.path.exists")
@patch("os.makedirs")
@patch("tqdm.tqdm")
def test_download_video(mock_tqdm, mock_makedirs, mock_exists, mock_glob, mock_youtube):
    mock_glob.return_value = []
    mock_exists.side_effect = [False, False]  # First for path existence, second for file existence
    mock_stream = MagicMock()
    mock_stream.default_filename = "test.mp4"
    mock_stream.filesize = 1024
    mock_youtube.return_value.streams.filter.return_value.desc.return_value.first.return_value = mock_stream

    mock_pbar = MagicMock()
    mock_tqdm.return_value = mock_pbar

    video_url = "https://youtu.be/abc123"
    path = "/tmp/"
    result = download_video(video_url, path)

    assert result == os.path.join(path, "test.mp4")
    mock_makedirs.assert_called_once_with(path)
    mock_stream.download.assert_called_once_with(output_path=path)
    


@patch("app.services.video.video_service.YouTube")
@patch("app.services.video.video_service.glob.glob")
@patch("os.path.exists")
def test_download_video_existing_file(mock_exists, mock_glob, mock_youtube):
    mock_glob.return_value = ["/tmp/test.mp4"]
    mock_exists.return_value = True

    video_url = "https://youtu.be/abc123"
    path = "/tmp/"
    result = download_video(video_url, path)

    assert result == "/tmp/test.mp4"
    mock_youtube.assert_not_called()
    
def test_download_video_path():
    video_url = "invalid_url"
    path = "/tmp/"
    result = download_video(video_url, path)

    assert result == os.path.join(path, video_url)

@patch("app.services.video.video_service.YouTube")
def test_download_video_unavailable(mock_youtube):
    mock_youtube.side_effect = VideoUnavailable("Video unavailable")

    video_url = "https://youtu.be/abc123"
    path = "/tmp/"
    result = download_video(video_url, path)

    assert result is None
    mock_youtube.assert_called_once_with(video_url, on_progress_callback=ANY)

# Test get_transcript_vtt
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
    
@patch("app.services.video.video_service.YouTubeTranscriptApi.get_transcript")
def test_get_transcript_vtt_no_transcript(mock_get_transcript, tmp_path):
    video_url = "https://www.youtube.com/watch?v=test_id"
    transcript_path = tmp_path / "captions.vtt"
    
    mock_get_transcript.side_effect = NoTranscriptFound("test id", "test language code", "test transcript data")
    
    result = get_transcript_vtt(video_url, str(tmp_path))
    assert result is None
    assert not transcript_path.exists()
    
    
# Test format_timestamp
@pytest.mark.parametrize(
    "seconds, expected",
    [
        (0, "00:00.000"),
        (65.432, "01:05.432"),
        (3605.123, "01:00:05.123"),
    ],
)
def test_format_timestamp(seconds, expected):
    result = format_timestamp(seconds)
    assert result == expected
    
# Test _processText
def test__processText():
    text = "This is a test"
    result = _processText(text)
    assert result == "This is a test"
    
    result = _processText(text, 4)
    assert result == "This\nis a\ntest"

# Test clean_table_name
@pytest.mark.parametrize(
    "title, expected",
    [
        ("My Video Title", "My_Video_Title"),
        ("Video@123!", "Video123"),
        ("Title with spaces", "Title_with_spaces"),
    ],
)
def test_clean_table_name(title, expected):
    result = clean_table_name(title)
    assert result == expected

# Test get_youtube_title
@patch("app.services.video.video_service.YoutubeDL.extract_info")
def test_get_youtube_title(mock_youtubedl_extract_info):
    mock_youtubedl_extract_info.return_value = {"title": "Test Video"}
    result = get_youtube_title("https://youtu.be/abc123")
    assert result == "Test Video"

# Test encode_image_to_base64
@patch("builtins.open", new_callable=mock_open, read_data=b"image_data")
def test_encode_image_to_base64(mock_open_file):
    result = encode_image_to_base64("test.jpg")
    assert result == "aW1hZ2VfZGF0YQ=="
    mock_open_file.assert_called_once_with("test.jpg", "rb")

# Test write_vtt with valid transcript
def test_write_vtt_valid_transcript(tmp_path):
    transcript = [
        {"start": 0.0, "end": 1.0, "text": "Hello world"},
        {"start": 1.0, "end": 2.0, "text": "This is a test"},
    ]
    vtt_path = tmp_path / "captions.vtt"
    with open(vtt_path, "w") as file:
        write_vtt(transcript, file)

    assert vtt_path.exists()
    with open(vtt_path, "r") as f:
        content = f.read()
        assert "WEBVTT" in content
        assert "00:00.000 --> 00:01.000" in content
        assert "Hello world" in content
        assert "00:01.000 --> 00:02.000" in content
        assert "This is a test" in content

# Test write_vtt with empty transcript
def test_write_vtt_empty_transcript(tmp_path):
    transcript = []
    vtt_path = tmp_path / "captions.vtt"
    with open(vtt_path, "w") as file:
        write_vtt(transcript, file)

    assert vtt_path.exists()
    with open(vtt_path, "r") as f:
        content = f.read()
        assert content.strip() == "WEBVTT"

# Test write_vtt with maxLineWidth
def test_write_vtt_with_max_line_width(tmp_path):
    transcript = [
        {"start": 0.0, "end": 1.0, "text": "This is a very long line of text that should be wrapped."},
    ]
    vtt_path = tmp_path / "captions.vtt"
    with open(vtt_path, "w") as file:
        write_vtt(transcript, file, maxLineWidth=20)

    assert vtt_path.exists()
    with open(vtt_path, "r") as f:
        content = f.read()
        assert "WEBVTT" in content
        assert "00:00.000 --> 00:01.000" in content
        assert "This is a very long" in content
        assert "line of text that" in content
        assert "should be wrapped." in content

# Test getSubs with VTT format
def test_getSubs_vtt_format():
    segments = [
        {"start": 0.0, "end": 1.0, "text": "Hello world"},
        {"start": 1.0, "end": 2.0, "text": "This is a test"},
    ]
    result = getSubs(segments, format="vtt")
    assert "WEBVTT" in result
    assert "00:00.000 --> 00:01.000" in result
    assert "Hello world" in result
    assert "00:01.000 --> 00:02.000" in result
    assert "This is a test" in result

# Test getSubs with SRT format
def test_getSubs_srt_format():
    segments = [
        {"start": 0.0, "end": 1.0, "text": "Hello world"},
        {"start": 1.0, "end": 2.0, "text": "This is a test"},
    ]
    result = getSubs(segments, format="srt")
    assert "1" in result
    assert "00:00:00,000 --> 00:00:01,000" in result
    assert "Hello world" in result
    assert "2" in result
    assert "00:00:01,000 --> 00:00:02,000" in result
    assert "This is a test" in result

# Test getSubs with invalid format
def test_getSubs_invalid_format():
    segments = [
        {"start": 0.0, "end": 1.0, "text": "Hello world"},
    ]
    with pytest.raises(Exception, match="Unknown format invalid"):
        getSubs(segments, format="invalid")

# Test getSubs with maxLineWidth
def test_getSubs_with_max_line_width():
    segments = [
        {"start": 0.0, "end": 1.0, "text": "This is a very long line of text that should be wrapped."},
    ]
    result = getSubs(segments, format="vtt", maxLineWidth=20)
    assert "This is a very long" in result
    assert "line of text that" in result
    assert "should be wrapped." in result

# Test write_srt with valid transcript
def test_write_srt_valid_transcript(tmp_path):
    transcript = [
        {"start": 0.0, "end": 1.0, "text": "Hello world"},
        {"start": 1.0, "end": 2.0, "text": "This is a test"},
    ]
    srt_path = tmp_path / "captions.srt"
    with open(srt_path, "w") as file:
        write_srt(transcript, file)

    assert srt_path.exists()
    with open(srt_path, "r") as f:
        content = f.read()
        assert "1" in content
        assert "00:00:00,000 --> 00:00:01,000" in content
        assert "Hello world" in content
        assert "2" in content
        assert "00:00:01,000 --> 00:00:02,000" in content
        assert "This is a test" in content

# Test write_srt with empty transcript
def test_write_srt_empty_transcript(tmp_path):
    transcript = []
    srt_path = tmp_path / "captions.srt"
    with open(srt_path, "w") as file:
        write_srt(transcript, file)

    assert srt_path.exists()
    with open(srt_path, "r") as f:
        content = f.read()
        assert content.strip() == ""

# Test write_srt with maxLineWidth
def test_write_srt_with_max_line_width(tmp_path):
    transcript = [
        {"start": 0.0, "end": 1.0, "text": "This is a very long line of text that should be wrapped."},
    ]
    srt_path = tmp_path / "captions.srt"
    with open(srt_path, "w") as file:
        write_srt(transcript, file, maxLineWidth=20)

    assert srt_path.exists()
    with open(srt_path, "r") as f:
        content = f.read()
        assert "1" in content
        assert "00:00:00,000 --> 00:00:01,000" in content
        assert "This is a very long" in content
        assert "line of text that" in content
        assert "should be wrapped." in content

# Test extract_and_save_frames_and_metadata
@patch("app.services.video.video_service.cv2.VideoCapture")
@patch("app.services.video.video_service.webvtt.read")
@patch("app.services.video.video_service.maintain_aspect_ratio_resize")
@patch("app.services.video.video_service.cv2.imwrite")
@patch("builtins.open", new_callable=mock_open)
def test_extract_and_save_frames_and_metadata(
    mock_open_file, mock_imwrite, mock_resize, mock_webvtt_read, mock_video_capture, tmp_path
):
    # Mock video capture
    mock_video = MagicMock()
    mock_video.read.side_effect = [(True, "frame1"), (True, "frame2"), (False, None)]
    mock_video.set.return_value = None
    mock_video_capture.return_value = mock_video

    # Mock webvtt
    mock_transcripts = [
        MagicMock(start="00:00:01.000", end="00:00:02.000", text="Hello world"),
        MagicMock(start="00:00:03.000", end="00:00:04.000", text="This is a test"),
    ]
    mock_webvtt_read.return_value = mock_transcripts

    # Mock resize
    mock_resize.return_value = "resized_frame"

    # Paths
    path_to_video = "/path/to/video.mp4"
    path_to_transcript = "/path/to/captions.vtt"
    path_to_save_extracted_frames = tmp_path / "frames"
    path_to_save_extracted_frames.mkdir()
    path_to_save_metadatas = tmp_path / "metadata"
    path_to_save_metadatas.mkdir()

    # Call the function
    result = extract_and_save_frames_and_metadata(
        path_to_video,
        path_to_transcript,
        str(path_to_save_extracted_frames),
        str(path_to_save_metadatas),
    )

    # Assertions
    assert len(result) == 2
    assert result[0]["transcript"] == "Hello world"
    assert result[1]["transcript"] == "This is a test"
    assert mock_video.set.call_count == 2
    assert mock_imwrite.call_count == 2

# Test extract_and_save_frames_and_metadata_with_fps
@patch("app.services.video.video_service.cv2.VideoCapture")
@patch("app.services.video.video_service.maintain_aspect_ratio_resize")
@patch("app.services.video.video_service.cv2.imwrite")
@patch("builtins.open", new_callable=mock_open)
@patch("app.services.video.video_service.ollama_inference")
def test_extract_and_save_frames_and_metadata_with_fps(
    mock_ollama_inference, mock_open_file, mock_imwrite, mock_resize, mock_video_capture, tmp_path
):
    # Mock video capture
    mock_video = MagicMock()
    mock_video.read.side_effect = [(True, "frame1"), (True, "frame2"), (False, None)]
    mock_video.get.return_value = 30  # FPS
    mock_video_capture.return_value = mock_video

    # Mock resize
    mock_resize.return_value = "resized_frame"

    # Mock inference
    mock_ollama_inference.side_effect = ["Caption 1", "Caption 2"]

    # Paths
    path_to_video = "/path/to/video.mp4"
    path_to_save_extracted_frames = tmp_path / "frames"
    path_to_save_extracted_frames.mkdir()
    path_to_save_metadatas = tmp_path / "metadata"
    path_to_save_metadatas.mkdir()

    # Call the function
    result = extract_and_save_frames_and_metadata_with_fps(
        path_to_video,
        str(path_to_save_extracted_frames),
        str(path_to_save_metadatas),
        num_of_extracted_frames_per_second=1,
    )

    # Assertions
    assert len(result) == 1
    assert result[0]["transcript"] == "Caption 1"
    assert mock_video.read.call_count == 3
    assert mock_imwrite.call_count == 1
    assert mock_ollama_inference.call_count == 1

'''
# Test prompt_processing with valid input
def test_prompt_processing_valid_input():
    mock_retreived_results = MagicMock()
    mock_retreived_results.metadata = {
        'transcript': 'This is a test transcript.',
        'extracted_frame_path': '/path/to/frame.jpg',
    }
    input_data = {
        "retrieved_results": mock_retreived_results,
        "user_query": "What is shown in the image?",
    }

    
    result = prompt_processing(input_data)

    assert result["prompt"] == (
        "The transcript associated with the image is 'This is a test transcript.'. "
        "What is shown in the image?"
    )
    assert result["image"] == "/path/to/frame.jpg"

# Test prompt_processing with missing metadata
def test_prompt_processing_missing_metadata():
    input_data = {
        "retrieved_results": [
            {
                "metadata": {
                    "transcript": "This is a test transcript.",
                }
            }
        ],
        "user_query": "What is shown in the image?",
    }

    with pytest.raises(KeyError, match="extracted_frame_path"):
        prompt_processing(input_data)
'''

# Test prompt_processing with empty retrieved_results
def test_prompt_processing_empty_retrieved_results():
    input_data = {
        "retrieved_results": [],
        "user_query": "What is shown in the image?",
    }

    with pytest.raises(IndexError):
        prompt_processing(input_data)

# Test prompt_processing with missing user_query
def test_prompt_processing_missing_user_query():
    input_data = {
        "retrieved_results": [
            {
                "metadata": {
                    "transcript": "This is a test transcript.",
                    "extracted_frame_path": "/path/to/frame.jpg",
                }
            }
        ],
    }

    with pytest.raises(KeyError, match="user_query"):
        prompt_processing(input_data)