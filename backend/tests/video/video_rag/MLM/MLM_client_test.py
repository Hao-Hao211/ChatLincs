import pytest
from unittest.mock import patch, MagicMock
from app.services.video.video_rag.MLM.client import BaseClient, LocalLLMClient

class TestBaseClient:
    @pytest.fixture
    def base_client(self):
        # Create a subclass of BaseClient to test abstract methods
        class TestClient(BaseClient):
            def generate(self, prompt: str, image: str, **kwargs) -> str:
                return "Generated text"

        return TestClient()

    def test_base_client_initialization(self, base_client):
        assert base_client.connection_url == "http://127.0.0.1:8090"
        assert base_client.timeout == 60
        assert base_client.headers == {'Content-Type': 'application/json'}

    @patch("requests.get")
    def test_root(self, mock_get, base_client):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Welcome"
        mock_get.return_value = mock_response

        response = base_client.root()
        assert response.status_code == 200
        assert response.text == "Welcome"
        mock_get.assert_called_once_with("http://127.0.0.1:8090/")

    def test_generate_stream_not_implemented(self, base_client):
        with pytest.raises(NotImplementedError):
            base_client.generate_stream("Test prompt", "Test image")

    def test_generate_batch_not_implemented(self, base_client):
        with pytest.raises(NotImplementedError):
            base_client.generate_batch(["Test prompt"], ["Test image"])
            
class TestLocalLLMClient:
    
    @pytest.fixture
    def local_llm_client(self):
        return LocalLLMClient()

    def test_local_llm_client_initialization(self, local_llm_client):
        assert local_llm_client.connection_url == "http://127.0.0.1:8090"
        assert local_llm_client.timeout == 60
        assert local_llm_client.headers == {'Content-Type': 'application/json'}

    def test_filter_accepted_genkwargs(self, local_llm_client):
        kwargs = {
            "generate_kwargs": {
                "max_tokens": 100,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 50,
                "invalid_key": "value"
            }
        }
        filtered_kwargs = local_llm_client.filter_accepted_genkwargs(kwargs)
        assert filtered_kwargs == {
            "max_tokens": 100,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 50
        }

    @patch("app.services.video.video_rag.MLM.client.isBase64")
    @patch("app.services.video.video_rag.MLM.client.ollama_inference_without64")
    def test_generate_with_base64_image(self, mock_inference, mock_is_base64, local_llm_client):
        mock_is_base64.return_value = True
        mock_inference.return_value = "Generated text"

        prompt = "Test prompt"
        image = "base64_encoded_image"
        result = local_llm_client.generate(prompt, image)

        assert result == "Generated text"
        mock_is_base64.assert_called_once_with(image)
        mock_inference.assert_called_once_with(prompt=prompt, image=image)

    @patch("app.services.video.video_rag.MLM.client.isBase64")
    @patch("app.services.video.video_rag.MLM.client.encode_image_from_path_or_url")
    @patch("app.services.video.video_rag.MLM.client.ollama_inference_without64")
    def test_generate_with_image_path(self, mock_inference, mock_encode_image, mock_is_base64, local_llm_client):
        mock_is_base64.return_value = False
        mock_encode_image.return_value = "base64_encoded_image"
        mock_inference.return_value = "Generated text"

        prompt = "Test prompt"
        image = "/path/to/image.jpg"
        result = local_llm_client.generate(prompt, image)

        assert result == "Generated text"
        mock_is_base64.assert_called_once_with(image)
        mock_encode_image.assert_called_once_with(image)
        mock_inference.assert_called_once_with(prompt=prompt, image="base64_encoded_image")

    def test_generate_with_invalid_image(self, local_llm_client):
        prompt = "Test prompt"
        image = None

        with pytest.raises(AssertionError, match="the input image cannot be None, it must be either base64-encoded image or path/URL to image"):
            local_llm_client.generate(prompt, image)