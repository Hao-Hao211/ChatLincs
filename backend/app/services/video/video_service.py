import os
from io import StringIO
from pytubefix import YouTube, Stream
import webvtt
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from youtube_transcript_api.formatters import WebVTTFormatter
from tqdm import tqdm
import whisper
from moviepy import VideoFileClip
from .utils import str2time
from .video_rag.embeddings.bridgetower_embeddings import BridgeTowerEmbeddings
import lancedb
import cv2
import json
from .utils import maintain_aspect_ratio_resize
from .utils import ollama_inference
import glob
from typing import Iterator, TextIO, List, Dict, Any, Optional, Sequence, Union
import textwrap
from yt_dlp import YoutubeDL
import re
from .video_rag.vectorstores.multimodal_lancedb import MultimodalLanceDB
from os import path as osp
import base64

def load_json_file(file_path):
    # Open the JSON file in read mode
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def get_video_id_from_url(video_url):
    import urllib.parse
    url = urllib.parse.urlparse(video_url)
    if url.hostname == 'youtu.be':
        return url.path[1:]
    if url.hostname in ('www.youtube.com', 'youtube.com'):
        if url.path == '/watch':
            p = urllib.parse.parse_qs(url.query)
            return p['v'][0]
        if url.path[:7] == '/embed/':
            return url.path.split('/')[2]
        if url.path[:3] == '/v/':
            return url.path.split('/')[2]

    return video_url

def download_video_with_filecheck(video_url, path='/tmp/'):
    print(f'Getting video information for {video_url}')
    if not video_url.startswith('http'):
        return os.path.join(path, video_url)

    filepath = glob.glob(os.path.join(path, '*.mp4'))
    if len(filepath) > 0:
        return filepath[0]

    def progress_callback(stream: Stream, data_chunk: bytes, bytes_remaining: int) -> None:
        pbar.update(len(data_chunk))

    yt = YouTube(video_url, on_progress_callback=progress_callback)
    stream = yt.streams.filter(progressive=True, file_extension='mp4', res='720p').desc().first()
    if stream is None:
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    if not os.path.exists(path):
        os.makedirs(path)
    filepath = os.path.join(path, stream.default_filename)
    if not os.path.exists(filepath):
        print('Downloading video from YouTube...')
        pbar = tqdm(desc='Downloading video from YouTube', total=stream.filesize, unit="bytes")
        stream.download(path)
        pbar.close()
    return filepath

def download_video(video_url, path='/tmp/'):
    print(f'Getting video information for {video_url}')
    if not video_url.startswith('http'):
        return os.path.join(path, video_url)

    filepath = glob.glob(os.path.join(path, '*.mp4'))
    if len(filepath) > 0:
        return filepath[0]

    def progress_callback(stream: Stream, data_chunk: bytes, bytes_remaining: int) -> None:
        pbar.update(len(data_chunk))
    try:
        yt = YouTube(video_url, on_progress_callback=progress_callback)
    except VideoUnavailable:
        print(f"Video unavailable: {video_url}")
        return None
    except Exception as e:
        print(f"Error fetching video: {e}")
        return None

    stream = yt.streams.filter(progressive=True, file_extension='mp4', res='720p').desc().first()

    if stream is None:
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

    if not os.path.exists(path):
        os.makedirs(path)

    filepath = os.path.join(path, stream.default_filename)

    if os.path.exists(filepath):
        print("Removing existing file before re-downloading...")
        os.remove(filepath)

    print('Downloading video from YouTube...')

    try:
        pbar = tqdm(desc='Downloading video from YouTube', total=stream.filesize, unit="bytes")
        stream.download(output_path=path)
        pbar.close()
    except Exception as e:
        print(f"Error during download: {e}")
        return None

    return filepath

# if this has transcript then download
def get_transcript_vtt(video_url, path='/tmp'):
    video_id = get_video_id_from_url(video_url)
    filepath = os.path.join(path,'captions.vtt')
    if os.path.exists(filepath):
        return filepath
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en-GB', 'en'])
    except (TranscriptsDisabled, NoTranscriptFound):
        print(f"No transcript available for video: {video_url}")
        return None

    formatter = WebVTTFormatter()
    webvtt_formatted = formatter.format_transcript(transcript)

    with open(filepath, 'w', encoding='utf-8') as webvtt_file:
        webvtt_file.write(webvtt_formatted)
    webvtt_file.close()

    return filepath


def format_timestamp(seconds: float, always_include_hours: bool = False, fractionalSeperator: str = '.'):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d}{fractionalSeperator}{milliseconds:03d}"

def _processText(text: str, maxLineWidth=None):
    if (maxLineWidth is None or maxLineWidth < 0):
        return text

    lines = textwrap.wrap(text, width=maxLineWidth, tabsize=4)
    return '\n'.join(lines)

def write_vtt(transcript: Iterator[dict], file: TextIO, maxLineWidth=None):
    print("WEBVTT\n", file=file)
    for segment in transcript:
        text = _processText(segment['text'], maxLineWidth).replace('-->', '->')

        print(
            f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}\n"
            f"{text}\n",
            file=file,
            flush=True,
        )
def getSubs(segments: Iterator[dict], format: str, maxLineWidth: int=-1) -> str:
    segmentStream = StringIO()

    if format == 'vtt':
        write_vtt(segments, file=segmentStream, maxLineWidth=maxLineWidth)
    elif format == 'srt':
        write_srt(segments, file=segmentStream, maxLineWidth=maxLineWidth)
    else:
        raise Exception("Unknown format " + format)

    segmentStream.seek(0)
    return segmentStream.read()

def write_srt(transcript: Iterator[dict], file: TextIO, maxLineWidth=None):
    for i, segment in enumerate(transcript, start=1):
        text = _processText(segment['text'].strip(), maxLineWidth).replace('-->', '->')

        # write srt lines
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True, fractionalSeperator=',')} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True, fractionalSeperator=',')}\n"
            f"{text}\n",
            file=file,
            flush=True,
        )

def extract_and_save_frames_and_metadata(
        path_to_video,
        path_to_transcript,
        path_to_save_extracted_frames,
        path_to_save_metadatas):

    metadatas = []

    video = cv2.VideoCapture(path_to_video)
    trans = webvtt.read(path_to_transcript)

    for idx, transcript in enumerate(trans):
        start_time_ms = str2time(transcript.start)
        end_time_ms = str2time(transcript.end)

        mid_time_ms = (end_time_ms + start_time_ms) / 2

        text = transcript.text.replace("\n", ' ')

        video.set(cv2.CAP_PROP_POS_MSEC, mid_time_ms)
        success, frame = video.read()
        if success:

            image = maintain_aspect_ratio_resize(frame, height=350)

            img_fname = f'frame_{idx}.jpg'
            img_fpath = osp.join(
                path_to_save_extracted_frames, img_fname
            )
            cv2.imwrite(img_fpath, image)

            metadata = {
                'extracted_frame_path': img_fpath,
                'transcript': text,
                'video_segment_id': idx,
                'video_path': path_to_video,
                'mid_time_ms': mid_time_ms,
            }
            metadatas.append(metadata)

        else:
            print(f"ERROR! Cannot extract frame: idx = {idx}")

    fn = osp.join(path_to_save_metadatas, 'metadatas.json')
    with open(fn, 'w') as outfile:
        json.dump(metadatas, outfile)
    return metadatas


def extract_and_save_frames_and_metadata_with_fps(
        path_to_video,
        path_to_save_extracted_frames,
        path_to_save_metadatas,
        num_of_extracted_frames_per_second=1):
    # metadatas will store the metadata of all extracted frames
    metadatas = []

    video = cv2.VideoCapture(path_to_video)

    # Get the frames per second
    fps = video.get(cv2.CAP_PROP_FPS)
    # Get hop = the number of frames pass before a frame is extracted
    hop = round(fps / num_of_extracted_frames_per_second)
    curr_frame = 0
    idx = -1
    while (True):
        # iterate all frames
        ret, frame = video.read()
        if not ret:
            break
        if curr_frame % hop == 0:
            idx = idx + 1

            # if the frame is extracted successfully, resize it
            image = maintain_aspect_ratio_resize(frame, height=350)
            # save frame as JPEG file
            img_fname = f'frame_{idx}.jpg'
            img_fpath = osp.join(
                path_to_save_extracted_frames,
                img_fname
            )
            cv2.imwrite(img_fpath, image)

            # generate caption using lvlm_inference
            # b64_image = encode_image(img_fpath)
            caption = ollama_inference("Can you describe the image?", img_fpath)

            metadata = {
                'extracted_frame_path': img_fpath,
                'transcript': caption,
                'video_segment_id': idx,
                'video_path': path_to_video,
            }
            metadatas.append(metadata)
        curr_frame += 1

    # save metadata of all extracted frames
    metadatas_path = osp.join(path_to_save_metadatas, 'metadatas.json')
    with open(metadatas_path, 'w') as outfile:
        json.dump(metadatas, outfile)
    return metadatas

def extract_audio_and_transcribe(video_filepath, audio_output_path):
    clip = VideoFileClip(video_filepath)
    clip.audio.write_audiofile(audio_output_path)
    model = whisper.load_model("small")
    result = model.transcribe(audio_output_path, task="translate", language='en')
    return result["text"], result["segments"]

def extract_and_save_frames(
        path_to_video,
        path_to_save_extracted_frames,
        path_to_save_metadatas,
        num_of_extracted_frames_per_second=1):

    # metadatas will store the metadata of all extracted frames
    metadatas = []

    video = cv2.VideoCapture(path_to_video)

    # Get the frames per second
    fps = video.get(cv2.CAP_PROP_FPS)
    # Get hop = the number of frames pass before a frame is extracted
    hop = round(fps / num_of_extracted_frames_per_second)
    curr_frame = 0
    idx = -1
    while(True):
        ret, frame = video.read()
        if not ret:
            break
        if curr_frame % hop == 0:
            idx = idx + 1

            # if the frame is extracted successfully, resize it
            image = maintain_aspect_ratio_resize(frame, height=350)

            img_fname = f'frame_{idx}.jpg'
            img_fpath = osp.join(
                            path_to_save_extracted_frames,
                            img_fname
                        )
            cv2.imwrite(img_fpath, image)

            # generate caption using lvlm_inference
            # b64_image = encode_image(img_fpath)
            caption = ollama_inference("Can you describe the image?", img_fpath)

            # prepare the metadata
            metadata = {
                'extracted_frame_path': img_fpath,
                'transcript': caption,
                'video_segment_id': idx,
                'video_path': path_to_video,
            }
            metadatas.append(metadata)
        curr_frame += 1

    # save metadata of all extracted frames
    metadatas_path = osp.join(path_to_save_metadatas,'metadatas.json')
    with open(metadatas_path, 'w') as outfile:
        json.dump(metadatas, outfile)
    return metadatas

def embed_and_store_multimodal(metadata, lancedb_host, table_name, mode="append"):
    embedder = BridgeTowerEmbeddings()
    texts = [item['transcript'] for item in metadata]
    image_paths = [item['extracted_frame_path'] for item in metadata]

    db = lancedb.connect(lancedb_host)
    MultimodalLanceDB.from_text_image_pairs(
        texts=texts,
        image_paths=image_paths,
        embedding=embedder,
        metadatas=metadata,
        connection=db,
        table_name=table_name,
        mode=mode
    )

def get_youtube_title(video_url):
    ydl_opts = {'quiet': True}
    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        return info_dict.get('title', 'untitled_video')

def clean_table_name(title):
    title = title.replace(' ', '_')
    title = re.sub(r'[^a-zA-Z0-9_\-\.]', '', title)
    return title

def prompt_processing(input):
    retrieved_results = input['retrieved_results']
    user_query = input['user_query']

    retrieved_result = retrieved_results[0]
    prompt_template = (
      "The transcript associated with the image is '{transcript}'. "
      "{user_query}"
    )

    retrieved_metadata = retrieved_result.metadata

    transcript = retrieved_metadata['transcript']
    frame_path = retrieved_metadata['extracted_frame_path']

    return {
        'prompt': prompt_template.format(
            transcript=transcript,
            user_query=user_query
        ),
        'image' : frame_path
    }

def encode_image_to_base64(img_path):
    with open(img_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')