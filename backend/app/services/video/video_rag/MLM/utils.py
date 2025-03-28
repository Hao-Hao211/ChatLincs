from typing import Iterator, TextIO, List, Dict, Any, Optional, Sequence, Union
import base64
from urllib.request import urlopen
import requests
from langchain_core.prompt_values import PromptValue
from langchain_core.messages import (
    MessageLikeRepresentation,
)

MultimodalModelInput = Union[PromptValue, str, Sequence[MessageLikeRepresentation], Dict[str, Any]]

# checking whether the given string is base64 or not
def isBase64(sb):
    try:
        if isinstance(sb, str):
                # If there's any unicode here, an exception will be thrown and the function will return false
                sb_bytes = bytes(sb, 'ascii')
        elif isinstance(sb, bytes):
                sb_bytes = sb
        else:
                raise ValueError("Argument must be string or bytes")
        return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
    except Exception:
            return False

def encode_image_from_path_or_url(image_path_or_url):
    try:
        f = urlopen(image_path_or_url)
        return base64.b64encode(requests.get(image_path_or_url).content).decode('utf-8')
    except:
        with open(image_path_or_url, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

import ollama
def ollama_inference_without64(prompt, image, **kwargs):

    response = ollama.chat(
        model='llava:7b',
        messages=[{
            'role': 'user',
            'content': prompt,
            'images': [image]
        }]
    )
    return response.message['content']