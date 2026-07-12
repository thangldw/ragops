import io
import urllib.error
from unittest.mock import patch

import pytest

from ragops.adapters.http import AdapterError, post_json


class _Response:
    def __init__(self, body: bytes) -> None:
        self.body = io.BytesIO(body)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self) -> bytes:
        return self.body.read()


def test_post_json_returns_object() -> None:
    with patch("urllib.request.urlopen", return_value=_Response(b'{"answer":"ok"}')) as call:
        result = post_json("https://example.test/query", {"question": "q"})

    assert result == {"answer": "ok"}
    assert call.call_args.kwargs["timeout"] == 30.0


def test_post_json_wraps_transport_error() -> None:
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("offline")):
        with pytest.raises(AdapterError, match="HTTP adapter failed"):
            post_json("https://example.test/query", {})
