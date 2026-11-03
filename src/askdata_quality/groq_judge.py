"""
Groq LLM Judge for DeepEval
=============================
Custom DeepEval model that uses Groq's free API (llama-3.3-70b-versatile)
as the LLM-as-Judge for all evaluation metrics.

Groq free tier: https://console.groq.com
- No credit card required
- ~30 RPM, generous daily token budget
- OpenAI-compatible API
"""

from __future__ import annotations

import os
import time

from deepeval.models import DeepEvalBaseLLM
from groq import Groq


class GroqJudge(DeepEvalBaseLLM):
    """
    DeepEval-compatible LLM wrapper for Groq's free inference API.

    Usage:
        judge = GroqJudge(model_name="llama-3.3-70b-versatile")
        metric = AnswerRelevancyMetric(model=judge, threshold=0.7)
    """

    def __init__(
        self,
        model_name: str = "llama-3.3-70b-versatile",
        api_key: str | None = None,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        self.model_name = model_name
        self._api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client = Groq(api_key=self._api_key)

    def load_model(self):
        """Return the Groq client instance."""
        return self.client

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Synchronous generation with retry logic for rate limiting.

        Groq free tier has rate limits (~30 RPM). We implement
        exponential backoff to handle 429 responses gracefully.
        """
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a precise evaluation assistant. "
                                "Follow all formatting instructions exactly. "
                                "Output only what is requested."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.0,
                    max_tokens=4096,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    wait = self.retry_delay * (2**attempt)
                    time.sleep(wait)
                    continue
                raise
        return ""

    async def a_generate(self, prompt: str, **kwargs) -> str:
        """
        Async generation — falls back to sync for Groq client.

        DeepEval calls this for async metric evaluation.
        The Groq Python SDK's sync client works fine here since
        the I/O is fast (Groq's LPU inference is sub-second).
        """
        return self.generate(prompt, **kwargs)

    def get_model_name(self) -> str:
        """Return the model identifier for reporting."""
        return f"groq/{self.model_name}"
