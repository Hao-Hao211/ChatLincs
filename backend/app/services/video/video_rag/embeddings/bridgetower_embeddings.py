from typing import List
from langchain_core.embeddings import Embeddings
from langchain_core.pydantic_v1 import (
    BaseModel,
)
from .utils import bt_embedding_local2
from PIL import Image
import base64
from io import BytesIO

class BridgeTowerEmbeddings(BaseModel, Embeddings):

    def create_dummy_base64_image(self):
        dummy_img = Image.new("RGB", (224, 224), color="white")
        buffered = BytesIO()
        dummy_img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        dummy_image_b64 = self.create_dummy_base64_image()
        embeddings = []
        for text in texts:
            embedding = bt_embedding_local2(text, dummy_image_b64)
            embeddings.append(embedding)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]