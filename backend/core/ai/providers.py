from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


@dataclass
class AIResponse:
	text: str = ""
	embeddings: Optional[List[float]] = None
	usage: Dict[str, int] = None
	status_code: int = 200
	provider_error: Optional[str] = None


class BaseProvider:
	def __init__(self, api_key: str, base_url: str | None = None):
		self.api_key = api_key
		self.base_url = base_url

	def generate(self, model: str, prompt: str, max_tokens: int = 512) -> AIResponse:
		raise NotImplementedError

	def embed(self, model: str, texts: List[str]) -> AIResponse:
		raise NotImplementedError


class OpenAICompatibleProvider(BaseProvider):
	"""Kompatibilitäts-Client für OpenAI-ähnliche APIs (OpenAI, Groq, Local-Server)."""

	def _headers(self) -> Dict[str, str]:
		return {
			"Authorization": f"Bearer {self.api_key}",
			"Content-Type": "application/json",
		}

	def _base(self) -> str:
		return self.base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

	def generate(self, model: str, prompt: str, max_tokens: int = 512) -> AIResponse:
		body = {
			"model": model,
			"messages": [{"role": "user", "content": prompt}],
			"max_tokens": max_tokens,
		}
		try:
			with httpx.Client(timeout=60.0) as client:
				r = client.post(f"{self._base()}/chat/completions", headers=self._headers(), json=body)
				if r.status_code >= 400:
					return AIResponse(text="", usage={}, status_code=r.status_code, provider_error=r.text)
				data = r.json()
				text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
				usage = data.get("usage", {})
				return AIResponse(text=text, usage={
					"prompt_tokens": usage.get("prompt_tokens", 0),
					"completion_tokens": usage.get("completion_tokens", 0),
				})
		except Exception as e:
			return AIResponse(text="", usage={}, status_code=500, provider_error=str(e))

	def embed(self, model: str, texts: List[str]) -> AIResponse:
		body = {"model": model, "input": texts}
		try:
			with httpx.Client(timeout=60.0) as client:
				r = client.post(f"{self._base()}/embeddings", headers=self._headers(), json=body)
				if r.status_code >= 400:
					return AIResponse(embeddings=None, usage={}, status_code=r.status_code, provider_error=r.text)
				data = r.json()
				vecs = [item.get("embedding", []) for item in data.get("data", [])]
				usage = data.get("usage", {})
				return AIResponse(embeddings=vecs[0] if vecs else [], usage={
					"prompt_tokens": usage.get("prompt_tokens", 0),
					"completion_tokens": usage.get("completion_tokens", 0),
				})
		except Exception as e:
			return AIResponse(embeddings=None, usage={}, status_code=500, provider_error=str(e))


def get_provider(provider: str, api_key: str, base_url: str | None) -> BaseProvider:
	# OpenAI/Groq/Local sind alle über OpenAI-kompatible Endpunkte angebunden
	return OpenAICompatibleProvider(api_key=api_key, base_url=base_url)

