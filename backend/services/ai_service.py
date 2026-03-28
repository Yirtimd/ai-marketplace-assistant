"""
AI Service

Service layer for AI providers integration.
Implements text, image and video generation entry points for workflows.
"""

from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from config import get_logger, settings

logger = get_logger(__name__)


class AIServiceError(Exception):
    """Base exception for AI service errors."""


class AIConfigurationError(AIServiceError):
    """Raised when AI provider is not configured."""


class AIService:
    """
    Unified AI service for different providers.

    Priority:
    1) DeepSeek (if configured)
    2) OpenAI (if configured)
    3) Anthropic (if configured)
    """

    def __init__(self):
        self.deepseek_api_key = settings.deepseek_api_key
        self.deepseek_base_url = settings.deepseek_base_url
        self.deepseek_model = settings.deepseek_model

        self.openai_api_key = settings.openai_api_key
        self.openai_model = settings.openai_model
        self.openai_image_model = settings.openai_image_model

        self.anthropic_api_key = settings.anthropic_api_key
        self.anthropic_model = settings.anthropic_model

        self._deepseek_client: Optional[AsyncOpenAI] = None
        self._openai_client: Optional[AsyncOpenAI] = None
        self._anthropic_client: Optional[AsyncAnthropic] = None

        logger.info("AIService initialized")

    def _has_text_provider(self) -> bool:
        return bool(self.deepseek_api_key or self.openai_api_key or self.anthropic_api_key)

    def _get_deepseek_client(self) -> AsyncOpenAI:
        if not self.deepseek_api_key:
            raise AIConfigurationError("DeepSeek API key is not configured")
        if self._deepseek_client is None:
            self._deepseek_client = AsyncOpenAI(
                api_key=self.deepseek_api_key,
                base_url=self.deepseek_base_url,
            )
        return self._deepseek_client

    def _get_openai_client(self) -> AsyncOpenAI:
        if not self.openai_api_key:
            raise AIConfigurationError("OpenAI API key is not configured")
        if self._openai_client is None:
            self._openai_client = AsyncOpenAI(api_key=self.openai_api_key)
        return self._openai_client

    def _get_anthropic_client(self) -> AsyncAnthropic:
        if not self.anthropic_api_key:
            raise AIConfigurationError("Anthropic API key is not configured")
        if self._anthropic_client is None:
            self._anthropic_client = AsyncAnthropic(api_key=self.anthropic_api_key)
        return self._anthropic_client

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 800,
    ) -> Dict[str, Any]:
        """
        Generate text using available AI provider.
        """
        if not prompt.strip():
            raise AIServiceError("Prompt must not be empty")

        if not self._has_text_provider():
            raise AIConfigurationError("No text AI provider configured")

        provider_errors: List[str] = []

        # 1) DeepSeek (OpenAI-compatible API)
        if self.deepseek_api_key:
            try:
                client = self._get_deepseek_client()
                response = await client.chat.completions.create(
                    model=model or self.deepseek_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                )
                text = (response.choices[0].message.content or "").strip()
                return {
                    "provider": "deepseek",
                    "model": model or self.deepseek_model,
                    "text": text,
                    "usage": getattr(response, "usage", None),
                    "status": "completed",
                }
            except Exception as exc:
                provider_errors.append(f"deepseek: {exc}")
                logger.warning("DeepSeek text generation failed: %s", exc)

        # 2) OpenAI
        if self.openai_api_key:
            try:
                client = self._get_openai_client()
                response = await client.chat.completions.create(
                    model=model or self.openai_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    messages=[
                        {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                )
                text = (response.choices[0].message.content or "").strip()
                return {
                    "provider": "openai",
                    "model": model or self.openai_model,
                    "text": text,
                    "usage": getattr(response, "usage", None),
                    "status": "completed",
                }
            except Exception as exc:
                provider_errors.append(f"openai: {exc}")
                logger.warning("OpenAI text generation failed: %s", exc)

        # 3) Anthropic
        if self.anthropic_api_key:
            try:
                client = self._get_anthropic_client()
                response = await client.messages.create(
                    model=model or self.anthropic_model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt or "You are a helpful assistant.",
                    messages=[{"role": "user", "content": prompt}],
                )
                text_chunks = []
                for chunk in response.content:
                    if hasattr(chunk, "text"):
                        text_chunks.append(chunk.text)
                text = "".join(text_chunks).strip()
                return {
                    "provider": "anthropic",
                    "model": model or self.anthropic_model,
                    "text": text,
                    "usage": getattr(response, "usage", None),
                    "status": "completed",
                }
            except Exception as exc:
                provider_errors.append(f"anthropic: {exc}")
                logger.warning("Anthropic text generation failed: %s", exc)

        raise AIServiceError(f"All text providers failed: {' | '.join(provider_errors)}")

    async def generate_images(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard",
    ) -> Dict[str, Any]:
        """
        Generate image asset via OpenAI Images API when available.
        """
        if not prompt.strip():
            raise AIServiceError("Prompt must not be empty")

        if not self.openai_api_key:
            return {
                "provider": "none",
                "prompt": prompt,
                "status": "queued_for_external_image_service",
                "note": "OpenAI API key is not configured",
            }

        try:
            client = self._get_openai_client()
            response = await client.images.generate(
                model=self.openai_image_model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
            )
            image_b64 = None
            image_url = None
            if response.data:
                image_b64 = getattr(response.data[0], "b64_json", None)
                image_url = getattr(response.data[0], "url", None)

            return {
                "provider": "openai",
                "model": self.openai_image_model,
                "prompt": prompt,
                "image_base64": image_b64,
                "image_url": image_url,
                "status": "completed",
            }
        except Exception as exc:
            logger.warning("Image generation failed: %s", exc)
            return {
                "provider": "openai",
                "prompt": prompt,
                "status": "queued_for_external_image_service",
                "error": str(exc),
            }

    async def generate_video(
        self,
        prompt: str,
        duration_seconds: int = 15,
    ) -> Dict[str, Any]:
        """
        Generate video payload.

        Video generation provider is intentionally abstracted for Stage 8.
        """
        if not prompt.strip():
            raise AIServiceError("Prompt must not be empty")

        return {
            "provider": "external_video_service",
            "prompt": prompt,
            "duration_seconds": duration_seconds,
            "status": "queued_for_external_video_service",
        }


# Singleton instance
ai_service = AIService()
