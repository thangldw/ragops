import pytest

from ragops.providers import OpenAIResponsesAdapter, ProviderError


def test_openai_responses_adapter_maps_request_and_usage() -> None:
    calls = []

    def transport(url, payload, *, headers):
        calls.append((url, payload, headers))
        return {
            "id": "resp_123",
            "model": "test-model-2026-01-01",
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "Grounded answer"}],
                }
            ],
            "usage": {"input_tokens": 10, "output_tokens": 3, "total_tokens": 13},
        }

    adapter = OpenAIResponsesAdapter(
        api_key="test-key",
        model="test-model-2026-01-01",
        transport=transport,
    )
    result = adapter.generate(input_text="Question", instructions="Cite evidence")

    assert result.text == "Grounded answer"
    assert result.usage["total_tokens"] == 13
    assert calls[0][0] == "https://api.openai.com/v1/responses"
    assert calls[0][1] == {
        "model": "test-model-2026-01-01",
        "input": "Question",
        "instructions": "Cite evidence",
    }
    assert calls[0][2]["authorization"] == "Bearer test-key"


def test_openai_responses_adapter_accepts_direct_output_text() -> None:
    adapter = OpenAIResponsesAdapter(
        api_key="test-key",
        model="test-model",
        transport=lambda *_args, **_kwargs: {
            "id": "resp_1",
            "output_text": "Direct text",
        },
    )

    assert adapter.generate(input_text="q").text == "Direct text"


def test_openai_responses_adapter_rejects_missing_text() -> None:
    adapter = OpenAIResponsesAdapter(
        api_key="test-key",
        model="test-model",
        transport=lambda *_args, **_kwargs: {"id": "resp_1", "output": []},
    )

    with pytest.raises(ProviderError, match="no output text"):
        adapter.generate(input_text="q")
