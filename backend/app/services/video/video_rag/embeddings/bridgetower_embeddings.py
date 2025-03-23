from typing import List
from langchain_core.embeddings import Embeddings
from langchain_core.pydantic_v1 import (
    BaseModel,
)
from .utils import bt_embedding_local2, encode_image
from PIL import Image
import base64
from io import BytesIO
from tqdm import tqdm

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

    def embed_image_text_pairs(self, texts: List[str], images: List[str], batch_size=2) -> List[List[float]]:
        """Embed a list of image-text pairs using BridgeTower.

        Args:
            texts: The list of texts to embed.
            images: The list of path-to-images to embed
            batch_size: the batch size to process, default to 2
        Returns:
            List of embeddings, one for each image-text pairs.
        """

        # the length of texts must be equal to the length of images
        assert len(texts)==len(images), "the len of captions should be equal to the len of images"

        embeddings = []
        for path_to_img, text in tqdm(zip(images, texts), total=len(texts)):
            # embedding = bt_embedding_from_prediction_guard(text, encode_image(path_to_img))
            embedding = bt_embedding_local2(text, encode_image(path_to_img))
            embeddings.append(embedding)
        return embeddings