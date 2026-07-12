import json
from pathlib import Path


def test_all_published_schemas_are_valid_json() -> None:
    schemas = sorted(Path("schemas").glob("*.json"))

    assert schemas
    for schema in schemas:
        document = json.loads(schema.read_text(encoding="utf-8"))
        assert document["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert document["$id"]
