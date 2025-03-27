import pytest
from unittest.mock import MagicMock, patch
from app.services.video.video_rag.MLM.lvlm import LVLM
from app.services.video.video_rag.MLM.utils import MultimodalModelInput
from langchain_core.prompt_values import StringPromptValue

pytest_plugins = ("pytest_asyncio",)

@pytest.fixture
def lvlm():
    client_mock = MagicMock()
    return LVLM(client=client_mock)

def test_llm_type(lvlm):
    assert lvlm._llm_type == "Large Vision Language Model"

def test_default_params(lvlm):
    default_params = lvlm._default_params
    assert default_params["max_tokens"] == 200
    assert default_params["temperature"] == 0.6
    assert default_params["top_k"] == 0
    assert default_params["ignore_eos"] is False
    assert default_params["do_sample"] is True
    assert default_params["stop"] is None

def test_get_params(lvlm):
    params = lvlm.get_params(temperature=0.8, max_tokens=100)
    assert params["temperature"] == 0.8
    assert params["max_tokens"] == 100

def test_call_method(lvlm):
    lvlm.client.generate.return_value = "Generated response"
    prompt = "Test prompt"
    image = "Test image"
    response = lvlm._call(prompt, image)
    assert response == "Generated response"
    lvlm.client.generate.assert_called_once_with(prompt=prompt, image=image, generate_kwargs=lvlm._default_params)

def test_call_method_with_stop(lvlm):
    with pytest.raises(ValueError, match="stop kwargs are not permitted."):
        lvlm._call("Test prompt", "Test image", stop=["stop"])

def test_stream_method(lvlm):
    lvlm.client.generate_stream.return_value = iter(["chunk1", "chunk2"])
    prompt = "Test prompt"
    image = "Test image"
    chunks = list(lvlm._stream(prompt, image))
    assert chunks == ["chunk1", "chunk2"]
    lvlm.client.generate_stream.assert_called_once_with(prompt=prompt, image=image, generate_kwargs=lvlm._default_params)

@pytest.mark.asyncio
@patch("app.services.video.video_rag.MLM.lvlm.run_in_executor")
async def test_astream_method_with_invalid_input(mock_run_in_executor, lvlm):
    with pytest.raises(ValueError, match="missing image is not permitted"):
        async for _ in lvlm.astream({"prompt": "Test prompt"}):
            pass

