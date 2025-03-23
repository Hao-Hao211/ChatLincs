from abc import ABC, abstractmethod
from typing import List, Optional, Iterator
import requests
from .utils import isBase64, encode_image_from_path_or_url
from .utils import ollama_inference_without64


class BaseClient(ABC):
    def __init__(self,
                 hostname: str = "127.0.0.1",
                 port: int = 8090,
                 timeout: int = 60,
                 url: Optional[str] = None):
        self.connection_url = f"http://{hostname}:{port}" if url is None else url
        self.timeout = timeout
        # self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.headers = {'Content-Type': 'application/json'}

    def root(self):
        """Request for showing welcome message"""
        connection_route = f"{self.connection_url}/"
        return requests.get(connection_route)

    @abstractmethod
    def generate(self, 
                 prompt: str,
                 image: str,
                 **kwargs
        ) -> str:
        """Send request to visual language model API
        and return generated text that was returned by the visual language model API
        """


    def generate_stream(
            self, 
            prompt: str, 
            image: str, 
            **kwargs
    ) -> Iterator[str]:

        raise NotImplementedError()
    
    def generate_batch(
            self, 
            prompt: List[str], 
            image: List[str], 
            **kwargs
    ) -> List[str]:

        raise NotImplementedError()
    
class LocalLLMClient(BaseClient):

    generate_kwargs = ['max_tokens', 
                       'temperature',
                       'top_p', 
                       'top_k']

    def filter_accepted_genkwargs(self, kwargs):
        gen_args = {}
        if "generate_kwargs" in kwargs and isinstance(kwargs["generate_kwargs"], dict):
            gen_args = {k:kwargs["generate_kwargs"][k] 
                        for k in self.generate_kwargs
                        if k in kwargs["generate_kwargs"]}
        return gen_args

    def generate(self,
                 prompt: str,
                 image: str,
                 **kwargs
        ) -> str:

        assert image is not None and len(image) != "", "the input image cannot be None, it must be either base64-encoded image or path/URL to image"
        if isBase64(image):
            base64_image = image
        else: # this is path to image or URL to image
            base64_image = encode_image_from_path_or_url(image)

        args = self.filter_accepted_genkwargs(kwargs)
        return ollama_inference_without64(prompt=prompt, image=base64_image, **args)
    