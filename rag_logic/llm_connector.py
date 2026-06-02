"""
SEPSES CSKG LLM Chatbot - LLM Connector

    Unified LLM connector using OpenRouter API.
    OpenRouter provides access to 100+ models from multiple providers
    through a single OpenAI-compatible API.

    Supported models include:
    - OpenAI: gpt-4o-mini, gpt-4o, gpt-3.5-turbo
    - Google: gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash
    - Anthropic: claude-3.5-sonnet, claude-3-haiku, claude-3-opus
    - Meta: llama-3-70b-instruct, llama-3-8b-instruct
    - Mistral: mistral-7b-instruct, mixtral-8x7b-instruct
    - And 100+ more: https://openrouter.ai/models
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
    """Representasi satu pesan dalam conversation."""

    ROLES = {"system", "user", "assistant"}

    def __init__(self, role: str, content: str) -> None:
        """
        Args:
            role   : "system" | "user" | "assistant"
            content: Teks pesan.

        Raises:
            ValueError: Jika role tidak valid.
        """
        if role not in self.ROLES:
            raise ValueError(f"Invalid role '{role}'. Must be one of: {self.ROLES}")
        self.role = role
        self.content = content

    def to_dict(self) -> dict:
        """Convert ke dict format yang kompatibel dengan OpenAI API."""
        return {"role": self.role, "content": self.content}

    def __repr__(self) -> str:
        return f"Message(role={self.role}, content={self.content[:50]!r})"


# Abstract Base Class
class BaseLLMConnector(ABC):
    """Abstract interface untuk semua LLM connectors."""

    @abstractmethod
    def generate(
        self,
        messages: List[Message],
        temperature: float = 0.2,
        max_tokens: int = 2048,
    ) -> str:
        """
        Generate respons dari LLM.

        Args:
            messages   : List of Message objects (system + user + history).
            temperature: Sampling temperature (0.0 = deterministic).
            max_tokens : Maksimum panjang output.

        Returns:
            str: Respons teks dari LLM.

        Raises:
            RuntimeError: Jika LLM tidak tersedia atau terjadi error.
        """
        ...

    @abstractmethod
    def ping(self) -> bool:
        """
        Cek apakah LLM backend tersedia.

        Returns:
            bool: True jika tersedia.
        """
        ...

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Nama model yang digunakan."""
        ...


# OpenRouter Connector
class OpenRouterConnector(BaseLLMConnector):
    """
    Unified connector to all LLM models via OpenRouter API.

    OpenRouter is a unified API gateway that provides access to 100+ models
    from OpenAI, Anthropic, Google, Meta, Mistral, and other providers
    through a single OpenAI-compatible interface.

    Environment variables yang diperlukan:
        OPENROUTER_API_KEY : OpenRouter API key (get from https://openrouter.ai/keys)
        OPENROUTER_MODEL   : Model identifier (default: openai/gpt-4o-mini)

    Model naming format: "provider/model-name"
    Examples:
        - "openai/gpt-4o-mini"
        - "google/gemini-2.0-flash"
        - "anthropic/claude-3.5-sonnet"
        - "meta-llama/llama-3-70b-instruct"
        - "mistralai/mistral-7b-instruct"
    """

    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        """
        Args:
            api_key: OpenRouter API key. Default dari env var OPENROUTER_API_KEY.
            model  : Model identifier. Default dari env var OPENROUTER_MODEL.

        Raises:
            RuntimeError: Jika openai package tidak terinstall atau API key kosong.
        """
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
        """
        Generate respons menggunakan OpenRouter API.

        Args:
            messages   : List of Message objects.
            temperature: Sampling temperature (0.0 - 2.0).
            max_tokens : Maximum tokens untuk respons.

        Returns:
            str: Respons teks dari model.

        Raises:
            RuntimeError: Jika API call gagal.
        """
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
        """
        Generate dengan pengukuran latency.

        Returns:
            tuple: (answer: str, latency_ms: float)
        """
        start = time.time()
        answer = self.generate(messages, temperature, max_tokens)
        latency = round((time.time() - start) * 1000, 2)
        return answer, latency

    def ping(self) -> bool:
        """
        Verifikasi koneksi ke OpenRouter API.

        Returns:
            bool: True jika API tersedia dan API key valid.
        """
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
    """
    Factory function untuk membuat LLM connector.

    Semua model sekarang diakses melalui OpenRouter API.
    Model name harus dalam format "provider/model-name".

    Args:
        llm_name: Nama model dalam format OpenRouter.
                  Examples:
                  - "openai/gpt-4o-mini"
                  - "google/gemini-2.0-flash"
                  - "anthropic/claude-3.5-sonnet"
                  - "meta-llama/llama-3-70b-instruct"
                  - "mistralai/mistral-7b-instruct"

                  Legacy names (untuk backward compatibility):
                  - "gpt-4o-mini" → "openai/gpt-4o-mini"
                  - "gpt-4o" → "openai/gpt-4o"
                  - "mistral" → "mistralai/mistral-7b-instruct"
                  - "gemini" → "google/gemini-2.0-flash"

    Returns:
        BaseLLMConnector: OpenRouter connector untuk model yang diminta.

    Raises:
        RuntimeError: Jika backend tidak tersedia.
    """
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
