import pytest
from unittest.mock import MagicMock, patch, ANY
from app.services.video.video_rag.vectorstores.multimodal_lancedb import MultimodalLanceDB

'''
def test_add_text_image_pairs_with_metadatas(multimodal_lancedb, mock_connection, mock_embedding):
    texts = ["Caption 1", "Caption 2"]
    image_paths = ["image1.jpg", "image2.jpg"]
    metadatas = [{"meta": "data1"}, {"meta": "data2"}]

    mock_table = MagicMock()
    mock_connection.table_names.return_value = ["vectorstore"]
    mock_connection.open_table.return_value = mock_table

    result_ids = multimodal_lancedb.add_text_image_pairs(texts, image_paths, metadatas=metadatas)

    assert len(result_ids) == len(texts)
    mock_embedding.embed_image_text_pairs.assert_called_once_with(texts=texts, images=image_paths)
    mock_table.add.assert_called_once()

def test_add_text_image_pairs_with_custom_mode(multimodal_lancedb, mock_connection, mock_embedding):
    texts = ["Caption 1", "Caption 2"]
    image_paths = ["image1.jpg", "image2.jpg"]

    mock_table = MagicMock()
    mock_connection.table_names.return_value = ["vectorstore"]
    mock_connection.open_table.return_value = mock_table

    result_ids = multimodal_lancedb.add_text_image_pairs(texts, image_paths, mode="overwrite")

    assert len(result_ids) == len(texts)
    mock_embedding.embed_image_text_pairs.assert_called_once_with(texts=texts, images=image_paths)
    mock_table.add.assert_called_once_with(ANY, mode="overwrite")

def test_from_text_image_pairs_creates_instance(mock_connection, mock_embedding):
    texts = ["Caption 1", "Caption 2"]
    image_paths = ["image1.jpg", "image2.jpg"]
    metadatas = [{"meta": "data1"}, {"meta": "data2"}]

    instance = MultimodalLanceDB.from_text_image_pairs(
        texts=texts,
        image_paths=image_paths,
        embedding=mock_embedding,
        metadatas=metadatas,
        connection=mock_connection,
        vector_key="vector",
        id_key="id",
        text_key="text",
        image_path_key="image_path",
        table_name="vectorstore"
    )

    assert isinstance(instance, MultimodalLanceDB)
    mock_embedding.embed_image_text_pairs.assert_called_once_with(texts=texts, images=image_paths)
'''