"""Interchangeable adapters; retry, validation and persistence belong to pipeline."""

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Protocol
from urllib.parse import urlparse

from dotenv import dotenv_values


class ProviderError(RuntimeError):
    def __init__(self, code, *, retryable=False, quota_exhausted=False):
        super().__init__(code)
        self.code = code
        self.retryable = retryable
        self.quota_exhausted = quota_exhausted


@dataclass
class ProviderResponse:
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    metadata: dict = field(default_factory=dict)


class Provider(Protocol):
    name: str
    model: str

    def generate(self, review, system_prompt, schema) -> ProviderResponse: ...


def api_key(root):
    """Return only to adapter. Never include this value in repr/logs/errors."""
    return os.environ.get("GEMINI_API_KEY") or dotenv_values(root / ".env").get(
        "GEMINI_API_KEY"
    )


def provider_error(exc):
    # Error bodies may contain user text or secrets. Persist only classified code.
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    if code == 429:
        return ProviderError("QUOTA_EXHAUSTED", quota_exhausted=True)
    if code in (401, 403):
        return ProviderError("AUTH_OR_PERMISSION_DENIED")
    if code == 404:
        return ProviderError("MODEL_UNAVAILABLE")
    if code in (408, 500, 502, 503, 504) or isinstance(exc, (TimeoutError, OSError)):
        return ProviderError("TRANSIENT_PROVIDER_ERROR", retryable=True)
    return ProviderError("PROVIDER_REQUEST_FAILED")


class GeminiProvider:
    name = "gemini"

    def __init__(self, root, model, execution, *, client=None):
        self.model = model
        self.execution = execution
        self._key = api_key(root)
        if client is None:
            if not self._key:
                raise ProviderError("GEMINI_API_KEY_MISSING")
            try:
                from google import genai
                from google.genai import types
            except ImportError:
                raise ProviderError("INSTALL_ANNOTATION_EXTRA") from None
            # Disable SDK retries: every request must pass our durable counter.
            client = genai.Client(
                api_key=self._key,
                vertexai=False,
                http_options=types.HttpOptions(
                    timeout=int(execution["timeout_seconds"] * 1000),
                    retry_options=types.HttpRetryOptions(attempts=1),
                ),
            )
        self.client = client

    def available(self):
        try:
            model = self.client.models.get(model=self.model)
            actions = getattr(model, "supported_actions", None)
            return {
                "model": self.model,
                "accessible": actions is None or "generateContent" in actions,
                "supported_actions": actions,
                "billing_verified_by_model_lookup": False,
            }
        except Exception as exc:  # noqa: BLE001 -- scrub arbitrary SDK error bodies
            raise provider_error(exc) from None

    def generate(self, review, system_prompt, schema):
        from google.genai import types

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=json.dumps(
                    {
                        "review_id": review["review_id"],
                        "review_text": review["review_text"],
                    },
                    ensure_ascii=False,
                ),
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    response_json_schema=schema,
                    temperature=self.execution["temperature"],
                    seed=self.execution["seed"],
                    max_output_tokens=self.execution["max_output_tokens"],
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=True
                    ),
                ),
            )
            usage = response.usage_metadata
            text = response.text
            if not text:
                raise ProviderError("EMPTY_OR_SAFETY_BLOCKED_OUTPUT")
            if self._key and self._key in text:
                raise ProviderError("SECRET_DETECTED_IN_RESPONSE")
            return ProviderResponse(
                text,
                getattr(usage, "prompt_token_count", None),
                getattr(usage, "candidates_token_count", None),
                getattr(usage, "total_token_count", None),
                {"model_version": getattr(response, "model_version", None)},
            )
        except ProviderError:
            raise
        except Exception as exc:  # noqa: BLE001 -- scrub arbitrary SDK error bodies
            raise provider_error(exc) from None

    def close(self):
        self.client.close()


class OllamaProvider:
    name = "ollama"

    def __init__(
        self,
        model="qwen2.5:3b",
        base_url="http://127.0.0.1:11434",
        timeout=60,
        execution=None,
    ):
        parsed = urlparse(base_url)
        if parsed.scheme != "http" or parsed.hostname not in (
            "localhost",
            "127.0.0.1",
            "::1",
        ):
            raise ProviderError("OLLAMA_MUST_BE_LOCAL")
        self.model, self.base_url, self.timeout = model, base_url.rstrip("/"), timeout
        self.execution = execution or {
            "temperature": 0,
            "seed": 42,
            "max_output_tokens": 6000,
        }

    def _request(self, route, payload=None):
        request = urllib.request.Request(
            self.base_url + route,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={"Content-Type": "application/json"},
        )
        # Ignore proxy variables for a local-only provider.
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(request, timeout=self.timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise ProviderError("OLLAMA_MODEL_NOT_INSTALLED") from None
            raise provider_error(exc) from None
        except (OSError, ValueError):
            raise ProviderError("OLLAMA_UNAVAILABLE", retryable=True) from None

    def available(self):
        models = [m["name"] for m in self._request("/api/tags").get("models", [])]
        return {
            "model": self.model,
            "accessible": self.model in models,
            "installed_models": models,
        }

    def generate(self, review, system_prompt, schema):
        obj = self._request(
            "/api/chat",
            {
                "model": self.model,
                "stream": False,
                "format": schema,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": json.dumps(
                            {
                                "review_id": review["review_id"],
                                "review_text": review["review_text"],
                            },
                            ensure_ascii=False,
                        ),
                    },
                ],
                "options": {
                    "temperature": self.execution["temperature"],
                    "seed": self.execution["seed"],
                    "num_predict": self.execution["max_output_tokens"],
                },
            },
        )
        return ProviderResponse(
            obj["message"]["content"],
            obj.get("prompt_eval_count"),
            obj.get("eval_count"),
            metadata={"model": obj.get("model")},
        )


class MockProvider:
    """Return explicitly authored synthetic responses, never label actual reviews."""

    name, model = "mock", "synthetic-fixtures-v1"

    def __init__(self, responses):
        self.responses = responses
        self.calls = 0

    def generate(self, review, system_prompt, schema):
        if review["data_origin"] != "synthetic":
            raise ProviderError("MOCK_REQUIRES_SYNTHETIC_REVIEW")
        self.calls += 1
        obj = self.responses[review["review_id"]]
        if isinstance(obj, list):
            obj = obj[min(self.calls - 1, len(obj) - 1)]
        if isinstance(obj, Exception):
            raise obj
        return ProviderResponse(
            obj if isinstance(obj, str) else json.dumps(obj), 0, 0, 0
        )
