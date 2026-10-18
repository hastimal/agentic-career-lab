## Description

<!-- Provide a brief description of the changes introduced in this PR. -->

Closes #<!-- issue number -->

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Observability / DevEx / CI improvement

## Privacy & Security Verification

- [ ] **Local-First Default:** Confirmed changes do not automatically trigger cloud endpoints without explicit consent.
- [ ] **No PII Leaks:** Confirmed raw resume text, PDF bytes, and personal identifiers are not exposed in telemetry, logs, or external requests.
- [ ] **Grounded AI:** Generative outputs are grounded against verified source evidence or catalog records.

## Checklist

- [ ] My code follows the code style of this project (`uv run ruff check .` passes).
- [ ] My code adheres to formatting guidelines (`uv run ruff format --check .` passes).
- [ ] I have added tests that prove my fix is effective or that my feature works (`uv run pytest` passes).
- [ ] I have updated documentation where necessary.
- [ ] If changing Streamlit UI or navigation, I verified interactions locally.
