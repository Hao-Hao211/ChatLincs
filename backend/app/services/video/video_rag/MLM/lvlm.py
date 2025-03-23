from langchain_core.language_models.llms import LLM
from typing import Any, Optional, List, Dict, Iterator, AsyncIterator
from .utils import  MultimodalModelInput

from langchain_core.runnables import RunnableConfig, ensure_config
from langchain_core.language_models.base import LanguageModelInput
from langchain_core.prompt_values import StringPromptValue
from langchain_core.language_models.llms import BaseLLM
from langchain_core.callbacks import (
    CallbackManagerForLLMRun,
)
from langchain_core.runnables.config import run_in_executor

class LVLM(LLM):
    client: Any = None #: :meta private:
    hostname: Optional[str] = None
    port: Optional[int] = None
    url: Optional[str] = None
    max_new_tokens: Optional[int] =  200
    temperature: Optional[float] = 0.6
    top_k: Optional[float] = 0
    stop: Optional[List[str]] = None
    ignore_eos: Optional[bool] = False
    do_sample: Optional[bool] = True
    lazy_mode: Optional[bool] = True
    hpu_graphs: Optional[bool] = True

    @property
    def _llm_type(self) -> str:
        return "Large Vision Language Model"

    @property
    def _default_params(self) -> Dict[str, Any]:
        return {
            "max_tokens": self.max_new_tokens,
            "temperature": self.temperature,
            "top_k": self.top_k,
            "ignore_eos": self.ignore_eos,
            "do_sample": self.do_sample,
            "stop" : self.stop,
        }

    def get_params(self, **kwargs):
        params = self._default_params
        params.update(kwargs)
        return params


    def _call(
        self,
        prompt: str,
        image: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        params = {}
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        params['generate_kwargs'] = self.get_params(**kwargs)
        response = self.client.generate(prompt=prompt, image=image, **params)
        return response

    def _stream(
        self,
        prompt: str,
        image: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        params = {}
        params['generate_kwargs'] = self.get_params(**kwargs)
        for chunk in self.client.generate_stream(prompt=prompt, image=image, **params):
            yield chunk

    async def _astream(
        self,
        prompt: str,
        image: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        iterator = await run_in_executor(
            None,
            self._stream,
            prompt,
            image,
            stop,
            run_manager.get_sync() if run_manager else None,
            **kwargs,
        )
        done = object()
        while True:
            item = await run_in_executor(
                None,
                next,
                iterator,
                done,  # type: ignore[call-arg, arg-type]
            )
            if item is done:
                break
            yield item  # type: ignore[misc]

    def invoke(
        self,
        input: MultimodalModelInput,
        config: Optional[RunnableConfig] = None,
        *,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        config = ensure_config(config)
        if isinstance(input, dict) and 'prompt' in input.keys() and 'image' in input.keys():
            return (
                self.generate_prompt(
                    [self._convert_input(StringPromptValue(text=input['prompt']))],
                    stop=stop,
                    callbacks=config.get("callbacks"),
                    tags=config.get("tags"),
                    metadata=config.get("metadata"),
                    run_name=config.get("run_name"),
                    run_id=config.pop("run_id", None),
                    image= input['image'],
                    **kwargs,
                )
                .generations[0][0]
                .text
            )
        return (
            self.generate_prompt(
                [self._convert_input(input)],
                stop=stop,
                callbacks=config.get("callbacks"),
                tags=config.get("tags"),
                metadata=config.get("metadata"),
                run_name=config.get("run_name"),
                run_id=config.pop("run_id", None),
                **kwargs,
            )
            .generations[0][0]
            .text
        )

    async def ainvoke(
        self,
        input: MultimodalModelInput,
        config: Optional[RunnableConfig] = None,
        *,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        config = ensure_config(config)
        if isinstance(input, dict) and 'prompt' in input.keys() and 'image' in input.keys():
            llm_result = await self.agenerate_prompt(
            [self._convert_input(StringPromptValue(text=input['prompt']))],
            stop=stop,
            callbacks=config.get("callbacks"),
            tags=config.get("tags"),
            metadata=config.get("metadata"),
            run_name=config.get("run_name"),
            run_id=config.pop("run_id", None),
            image=input['image'],
            **kwargs,
            )
        else:
            llm_result = await self.agenerate_prompt(
            [self._convert_input(input)],
            stop=stop,
            callbacks=config.get("callbacks"),
            tags=config.get("tags"),
            metadata=config.get("metadata"),
            run_name=config.get("run_name"),
            run_id=config.pop("run_id", None),
            **kwargs,
        )
        return llm_result.generations[0][0].text

    def stream(
        self,
        input: MultimodalModelInput,
        config: Optional[RunnableConfig] = None,
        *,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        if type(self)._stream == BaseLLM._stream:
            # model doesn't implement streaming, so use default implementation
            yield self.invoke(input, config=config, stop=stop, **kwargs)
        else:
            if stop is not None:
                raise ValueError("stop kwargs are not permitted.")
            image = None
            prompt = None
            if isinstance(input, dict) and 'prompt' in input.keys():
                prompt = self._convert_input(input['prompt']).to_string()
            else:
                raise ValueError("prompt must be provided")
            if isinstance(input, dict) and 'image' in input.keys():
                image = input['image']

            for chunk in self._stream(
                prompt=prompt, image=image, **kwargs
            ):
                yield chunk

    async def astream(
        self,
        input: LanguageModelInput,
        config: Optional[RunnableConfig] = None,
        *,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        if (
            type(self)._astream is BaseLLM._astream
            and type(self)._stream is BaseLLM._stream
        ):
            yield await self.ainvoke(input, config=config, stop=stop, **kwargs)
            return
        else:
            if stop is not None:
                raise ValueError("stop kwargs are not permitted.")
            image = None
            if isinstance(input, dict) and 'prompt' in input.keys() and 'image' in input.keys():
                prompt = self._convert_input(input['prompt']).to_string()
                image = input['image']
            else:
                raise ValueError("missing image is not permitted")
                prompt = self._convert_input(input).to_string()

            async for chunk in self._astream(
                prompt=prompt, image=image, **kwargs
            ):
                yield chunk