import json
from types import SimpleNamespace

import pytest

from brewscope.annotation.providers import (
    GeminiProvider,
    OllamaProvider,
    ProviderError,
    provider_error,
)
from brewscope.annotation.validation import inference_schema


class FakeModels:
    def __init__(self, response):
        self.response, self.arguments = response, None

    def get(self, **kwargs):
        return SimpleNamespace(supported_actions=["generateContent"])

    def generate_content(self, **kwargs):
        self.arguments = kwargs
        if isinstance(self.response, Exception):
            raise self.response
        return self.response


def test_sdk_structured_output_and_no_rating(root, config, one):
    review, obj = one
    fake = FakeModels(
        SimpleNamespace(
            text=json.dumps(obj),
            model_version="test-sdk",
            usage_metadata=SimpleNamespace(
                prompt_token_count=100, candidates_token_count=50, total_token_count=150
            ),
        )
    )
    provider = GeminiProvider(
        root, config["model"], config["execution"], client=SimpleNamespace(models=fake)
    )
    response = provider.generate(review, "system rules", inference_schema())
    assert response.total_tokens == 150 and provider.available()["accessible"]
    args = fake.arguments
    assert args["model"] == config["model"]
    assert args["config"].response_mime_type == "application/json"
    assert args["config"].response_json_schema == inference_schema()
    assert set(json.loads(args["contents"])) == {"review_id", "review_text"}
    assert args["config"].automatic_function_calling.disable


def test_missing_key_fails_without_network(tmp_path, config, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ProviderError, match="KEY_MISSING"):
        GeminiProvider(tmp_path, config["model"], config["execution"])


def test_error_cannot_expose_secret(root, config, one, monkeypatch):
    key = "SYNTHETIC_SECRET_NEVER_LOG"
    monkeypatch.setenv("GEMINI_API_KEY", key)
    fake = FakeModels(RuntimeError("server response includes " + key))
    provider = GeminiProvider(
        root, config["model"], config["execution"], client=SimpleNamespace(models=fake)
    )
    with pytest.raises(ProviderError) as caught:
        provider.generate(one[0], "prompt", inference_schema())
    assert key not in str(caught.value)
    assert key not in repr(provider)


def test_model_key_not_in_config(root):
    text = (root / "configs/annotation_runtime.yaml").read_text(encoding="utf8")
    assert "GEMINI_API_KEY=" not in text
    assert ".env" in (root / ".gitignore").read_text()


def test_429_stops_and_503_is_bounded_by_pipeline():
    assert provider_error(SimpleNamespace(code=429)).quota_exhausted
    assert provider_error(SimpleNamespace(code=503)).retryable
    assert not provider_error(SimpleNamespace(code=403)).retryable


def test_ollama_rejects_remote_endpoint():
    with pytest.raises(ProviderError, match="MUST_BE_LOCAL"):
        OllamaProvider(base_url="https://some-remote-provider.example")


def test_sdk_internal_retries_disabled(root, config, monkeypatch):
    from google import genai

    captured = {}

    def fake_client(**kwargs):
        captured.update(kwargs)
        return SimpleNamespace()

    monkeypatch.setenv("GEMINI_API_KEY", "SYNTHETIC_SECRET")
    monkeypatch.setattr(genai, "Client", fake_client)
    GeminiProvider(root, config["model"], config["execution"])
    assert captured["http_options"].retry_options.attempts == 1
    assert captured["vertexai"] is False
