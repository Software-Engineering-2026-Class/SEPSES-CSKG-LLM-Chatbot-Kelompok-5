"""
Unified LLM connector using OpenRouter API.
"""

import os
import time
from abc import ABC, abstractmethod
from typing import List, Optional

import structlog
from dotenv import load_dotenv

load_dotenv()
logger = structlog.get_logger(__name__)


# Message Type
class Message:

    ROLES = {"system", "user", "assistant"}

    def __init__(self, role: str, content: str) -> None:
  
        if role not in self.ROLES:
            raise ValueError(f"Invalid role '{role}'. Must be one of: {self.ROLES}")
        self.role = role
        self.content = content

    def to_dict(self) -> dict:
        return {"role": self.role, "content": self.content}

    def __repr__(self) -> str:
        return f"Message(role={self.role}, content={self.content[:50]!r})"


# Abstract Base Class
class BaseLLMConnector(ABC):


    @abstractmethod
    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        ...

    @abstractmethod
    def ping(self) -> bool:
        """Verifikasi koneksi ke LLM backend."""
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Nama model yang digunakan."""
        ...


# OpenRouter Connector
class OpenRouterConnector(BaseLLMConnector):
    """LLM connector untuk OpenRouter API (OpenAI-compatible)."""

    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        try:
            from openai import OpenAI

            self._api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
            if not self._api_key or self._api_key.startswith("sk-or-v1-GANTI"):
                raise RuntimeError(
                    "OPENROUTER_API_KEY belum diset! "
                    "Dapatkan API key dari https://openrouter.ai/keys "
                    "dan masukkan ke file .env"
                )

            self._model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

            # Initialize OpenAI client with OpenRouter base URL
            self._client = OpenAI(
                base_url=self.OPENROUTER_BASE_URL,
                api_key=self._api_key,
            )

            logger.info(
                "openrouter_connector_initialized",
                model=self._model,
                base_url=self.OPENROUTER_BASE_URL
            )

        except ImportError as exc:
            raise RuntimeError(
                "OpenAI SDK tidak terinstall! Run: pip install openai"
            ) from exc

    @property
    def model_name(self) -> str:
        """Return nama model yang digunakan."""
        return self._model

    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        try:
            # Convert Message objects to dict format
            msg_dicts = [m.to_dict() for m in messages]

            # Call OpenRouter API (OpenAI-compatible)
            response = self._client.chat.completions.create(
                model=self._model,
                messages=msg_dicts,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Extract answer
            answer = response.choices[0].message.content or ""

            logger.info(
                "openrouter_generate_success",
                model=self._model,
                tokens=response.usage.total_tokens if response.usage else 0,
                answer_length=len(answer)
            )

            return answer

        except Exception as exc:
            logger.error("openrouter_generate_error", error=str(exc), model=self._model)
            raise RuntimeError(f"OpenRouter API error: {exc}") from exc

    def generate_with_latency(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ):
        start = time.time()
        answer = self.generate(messages, temperature, max_tokens)
        latency = round((time.time() - start) * 1000, 2)
        return answer, latency

    def ping(self) -> bool:

        try:
            # Send minimal test request
            test_msg = [Message("user", "Hi")]
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[m.to_dict() for m in test_msg],
                max_tokens=5,
            )
            return bool(response.choices[0].message.content)
        except Exception as exc:
            logger.warning("openrouter_ping_failed", error=str(exc))
            return False


# Factory Function
def get_llm_connector(llm_name: str) -> BaseLLMConnector:
    
    # Normalize legacy model names to OpenRouter format
    model_mapping = {
        "gpt-4o-mini": "openai/gpt-4o-mini",
        "gpt-4o": "openai/gpt-4o",
        "gpt-3.5-turbo": "openai/gpt-3.5-turbo",
        "mistral": "mistralai/mistral-7b-instruct",
        "mistral-7b": "mistralai/mistral-7b-instruct",
        "gemini": "google/gemini-2.0-flash",
        "gemini-flash": "google/gemini-2.0-flash",
        "gemini-pro": "google/gemini-1.5-pro",
        "claude": "anthropic/claude-3.5-sonnet",
        "claude-sonnet": "anthropic/claude-3.5-sonnet",
        "claude-haiku": "anthropic/claude-3-haiku",
        "llama3": "meta-llama/llama-3-70b-instruct",
        "llama-3": "meta-llama/llama-3-70b-instruct",
    }

    # Check if it's a legacy name and convert it
    llm_lower = llm_name.lower()
    if llm_lower in model_mapping:
        openrouter_model = model_mapping[llm_lower]
        logger.info(
            "legacy_model_mapping",
            input=llm_name,
            mapped_to=openrouter_model
        )
    else:
        # Assume it's already in OpenRouter format
        openrouter_model = llm_name

    logger.info("creating_openrouter_connector", model=openrouter_model)
    return OpenRouterConnector(model=openrouter_model)
