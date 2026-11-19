# Contributing / Đóng góp / コントリビューション

- **English:** Preserve offline core semantics, version public schemas, add evidence fixtures and run `ruff check .` plus `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q`.
- **Tiếng Việt:** Giữ semantics offline của core, version public schema, thêm evidence fixture và chạy lint/test đầy đủ.
- **日本語:** オフラインコアの意味を維持し、公開 schema を version 管理し、証拠 fixture を追加して lint/test を実行してください。
- **Mutation testing:** `pip install -e '.[mutation]'`, then `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 mutmut run` and `mutmut results` (configured in `pyproject.toml` for calibration, explain, policy-suggest, CI renderers and the release policy engine `policy_v2`; delete `./mutants` afterwards). A surviving mutant is a behavior no test pins down: kill it with an exact-value or boundary test, or remove the redundant code. Current score on those modules: 2023 of 2340 mutants killed (about 86%); most survivors only change error-message text or letter case.
