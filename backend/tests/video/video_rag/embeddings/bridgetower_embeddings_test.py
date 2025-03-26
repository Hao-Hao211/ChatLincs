from unittest.mock import patch, MagicMock
from app.services.video.video_rag.embeddings.bridgetower_embeddings import BridgeTowerEmbeddings

def test_create_dummy_base64_image():
    embeddings = BridgeTowerEmbeddings()
    dummy_image = embeddings.create_dummy_base64_image()
    assert isinstance(dummy_image, str)
    assert dummy_image.startswith("/9j/")  # Check if it's a valid base64 JPEG header

@patch('app.services.video.video_rag.embeddings.bridgetower_embeddings.bt_embedding_local2')
def test_embed_documents(mock_bt_embedding_local2):
    mock_bt_embedding_local2.return_value = [0.1, 0.2, 0.3]
    embeddings = BridgeTowerEmbeddings()
    texts = ["Test text 1", "Test text 2"]
    result = embeddings.embed_documents(texts)
    assert len(result) == len(texts)
    assert result[0] == [0.1, 0.2, 0.3]
    mock_bt_embedding_local2.assert_called()

@patch('app.services.video.video_rag.embeddings.bridgetower_embeddings.bt_embedding_local2')
def test_embed_query(mock_bt_embedding_local2):
    mock_bt_embedding_local2.return_value = [0.1, 0.2, 0.3]
    embeddings = BridgeTowerEmbeddings()
    text = "Test query"
    result = embeddings.embed_query(text)
    assert result == [0.1, 0.2, 0.3]
    mock_bt_embedding_local2.assert_called_once()

@patch('app.services.video.video_rag.embeddings.bridgetower_embeddings.encode_image')
@patch('app.services.video.video_rag.embeddings.bridgetower_embeddings.bt_embedding_local2')
def test_embed_image_text_pairs(mock_bt_embedding_local2, mock_encode_image):
    mock_bt_embedding_local2.return_value = [0.1, 0.2, 0.3]
    mock_encode_image.return_value = "encoded_image"
    embeddings = BridgeTowerEmbeddings()
    texts = ["Caption 1", "Caption 2"]
    images = ["image1.jpg", "image2.jpg"]
    result = embeddings.embed_image_text_pairs(texts, images)
    assert len(result) == len(texts)
    assert result[0] == [0.1, 0.2, 0.3]
    mock_bt_embedding_local2.assert_called()
    mock_encode_image.assert_called()